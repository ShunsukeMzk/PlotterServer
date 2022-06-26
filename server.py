#!/usr/bin/env python

# WS server that sends messages at random intervals

import signal
import asyncio
import logging
import datetime
import random
import websockets
import os
import sys
import json
import secrets


PORT = os.getenv("PORT")
INIT = os.getenv("INIT")
LOG = os.getenv("LOG")

log = open(LOG, "a")


OBJECTS = dict()
FUNCTIONS = dict()
FIELDS = dict()

players = dict()
members = dict()


class Info:

    @property
    def fields(self):
        return [v for v in vars(self) if getattr(self, v) is not None]

    def __init__(self, message: str):
        self.type = ""
        self.path = ""
        self.target = ""
        for k, v in json.loads(message).items():
            setattr(self, k, v)

    def overwrite(self, info):
        for attr in info.fields:
            value = getattr(info, attr)
            if value is not None:
                setattr(self, attr, value)

    def to_dict(self):
        return {f: getattr(self, f) for f in self.fields if f != "from"}

    def to_json(self):
        return json.dumps(self.to_dict())


def apply(message) -> bool:
    try:
        json.loads(message)
        info = Info(message)

        def _apply(_key, _objects_, _info):
            if _key in _objects_:
                _objects_[_key].overwrite(_info)
            else:
                _objects_[_key] = _info

        if info.type.startswith("Object"):
            key = info.path
            _apply(key, OBJECTS, info)
        elif info.type.startswith("Function"):
            key = (info.target, info.type)
            _apply(key, FUNCTIONS, info)
        elif info.type.startswith("Field"):
            key = info.type
            _apply(key, FIELDS, info)
        elif info.type.startswith("Action"):
            if info.type == "Action/Player/Join":
                members[info.playerName] = info
        else:
            pass
    except json.decoder.JSONDecodeError:
        print(f"Invalid JSON message: {message}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected message: {message}, error: {e}", file=sys.stderr)
        return False
    else:
        return True


async def init(websocket, path):
    # Initialize Objects
    for info in OBJECTS.values():
        await websocket.send(info.to_json() + "\n")
    for info in FUNCTIONS.values():
        await websocket.send(info.to_json() + "\n")
    for info in FIELDS.values():
        await websocket.send(info.to_json() + "\n")
    for info in members.values():
        await websocket.send(info.to_json() + "\n")


async def broadcast(message, name):
    for _name in filter(lambda x: x != name, players):
        ws = players[_name]
        await ws.send(message)


async def handler(websocket, path):
    print(f"Connected: {path}", file=sys.stderr)
    name = path[1:]
    players[name] = websocket

    await init(websocket, path)

    async def _close():
        print(f"Connection Closed: {path}")
        msg = json.dumps(
            {
                "type": "Action/Player/Leave",
                "playerName": name,
            }
        )
        del_objects = []
        for obj_path in OBJECTS:
            if obj_path.startswith(name):
                del_objects.append(obj_path)
        for obj_path in del_objects:
            del OBJECTS[obj_path]
        await broadcast(msg, name)

    try:
        async for message in websocket:
            if message == "Close":
                await _close()
                return
            succeed = apply(message)
            if succeed:
                log.write(message + "\n")
                await broadcast(message, name)
                print("#", flush=True, end="")
    except websockets.ConnectionClosed:
        print(datetime.datetime.now())
        await _close()
    finally:
        del players[name]
        if name in members:
            del members[name]


async def main():

    # Initialize Object Information
    with open(INIT, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            apply(line)

    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    port = int(os.environ.get("PORT", "8080"))
    async with websockets.serve(handler, "0.0.0.0", port):
        await stop


if __name__ == "__main__":
    try:
        print(f"-- Start Server --", file=sys.stderr)
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"-- Stop Server --", file=sys.stderr)
