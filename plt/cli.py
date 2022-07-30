import asyncio
import click
import json
import os
import signal
import sys
import websockets
from datetime import datetime
from pathlib import Path

PLT_HOST = os.getenv("PLT_HOST", "localhost")
PLT_PORT = os.getenv("PLT_PORT", "8080")


def interrupt(async_func):
    async def wrapper():
        try:
            return await async_func()
        except KeyboardInterrupt:
            return
    return wrapper


@click.group()
def cli():
    pass


@cli.command()
def server():
    log = Path("plotter.log")
    if log.exists():
        mtime = datetime.fromtimestamp(log.stat().st_mtime)
        mtime = mtime.replace(microsecond=0)
        log.rename(Path(f"plotter.{mtime.isoformat()}.log"))
    log = log.open(mode="w")

    reconnect_time = 10

    players = {}  # name: websocket
    disconnected = {}  # name: task

    async def _get_master(name):
        for p in players.copy():
            if p == name:
                continue
            if p.startswith("_"):
                continue
            while p in disconnected:
                await asyncio.sleep(0.1)
            if p in players:
                return p

    async def _send(name, message):
        try:
            websocket = players[name]
            message = json.dumps(message)
            await websocket.send(message)
        except websockets.ConnectionClosed:
            click.echo(f"Failed to Send Message: {message}, To: {name}", err=True)

    async def _broadcast(name, message):
        for p in players.copy():
            if p == name:
                continue
            if p == "_sender":
                continue
            if p in disconnected:
                continue
            await _send(p, message)

    async def _task(name):
        websocket = players[name]
        async for message in websocket:
            try:
                message = message.rstrip("\n")
                log.write(f"{message}\n")
                log.flush()
                message = json.loads(message)
                click.echo("#", err=True, nl=False)
                await _broadcast(name, message)

                if message["type"] == "Action/Player/Leave":
                    _name = message["playerName"]
                    if _name in players:
                        click.echo(f"Leave: {_name}", err=True)
                        del players[_name]

            except json.decoder.JSONDecodeError:
                click.echo(f"Invalid JSON message: {message}", err=True)

    async def _join(name):
        click.echo(f"Join: {name}", err=True)

        master = await _get_master(name)
        if master:
            await _send(name, {"type": "Action/Delete/All"})
            await asyncio.sleep(2)
            await _send(master, {"type": "Action/Dump"})
        else:
            click.echo(f"Master Client: {name}", err=True)

    async def _leave(name):
        click.echo(f"Leave: {name}", err=True)
        del players[name]

        await _broadcast(
            name,
            {
                "type": "Action/Player/Leave",
                "playerName": name
            }
        )

    async def _disconnect(name):
        click.echo(f"Disconnect: {name}", err=True)

        if name not in players:
            return

        if name in disconnected:
            disconnected[name].cancel()

        async def __dc():
            await asyncio.sleep(reconnect_time)
            del disconnected[name]
            await _leave(name)

        task = asyncio.create_task(__dc())
        disconnected[name] = task

    async def _connect(websocket, path):
        name = path.split("/")[1]
        reconnect = name in players
        players[name] = websocket
        click.echo(f"Connect: {name}", err=True)

        if name in disconnected:
            disconnected[name].cancel()
            del disconnected[name]

        if not reconnect:
            await _join(name)

        task = asyncio.create_task(_task(name))
        try:
            await websocket.wait_closed()
        finally:
            task.cancel()
            await _disconnect(name)

    async def _serve():
        loop = asyncio.get_running_loop()
        stop = loop.create_future()
        loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
        async with websockets.serve(
                _connect,
                "0.0.0.0",
                int(PLT_PORT),
                ping_interval=None,
                ping_timeout=None
        ):
            await stop

    asyncio.run(_serve())


@cli.command()
@click.option("--file", "-f", type=click.File("a"), default=sys.stdout)
def receiver(file):
    uri = f"ws://{PLT_HOST}:{PLT_PORT}/_receiver"

    @interrupt
    async def _receive():
        async for websocket in websockets.connect(uri, ping_timeout=None):
            click.echo(f"Connected", err=True)
            try:
                while True:
                    message = await websocket.recv()
                    file.write(f"{message}\n")
                    file.flush()
            except websockets.ConnectionClosed:
                click.echo(f"Connection Closed and Retry Connect", err=True)

    asyncio.run(_receive())


@cli.command()
@click.option("--file", "-f", type=click.File("r"), default=sys.stdin)
def sender(file):
    uri = f"ws://{PLT_HOST}:{PLT_PORT}/_sender"

    @interrupt
    async def _send():
        last_message = ""
        async for websocket in websockets.connect(uri, ping_timeout=None):
            click.echo(f"Connected", err=True)
            await asyncio.sleep(0.05)
            try:
                if last_message:
                    await websocket.send(last_message)
                    last_message = ""
                for line in file:
                    if not line:
                        continue
                    last_message = line
                    await websocket.send(line)
                    last_message = ""
                click.echo(f"Send Complete", err=True)
                return
            except websockets.ConnectionClosed:
                click.echo(f"Connection Closed and Retry Connect", err=True)

    asyncio.run(_send())


if __name__ == "__main__":
    cli()


