#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
import datetime
import random
import websockets
import os
import sys
import json


PORT = os.getenv("PORT")

objects = {}
connections = {}


async def handler(websocket, path):
    consumer_task = asyncio.ensure_future(receiver(websocket, path))
    producer_task = asyncio.ensure_future(sender(websocket, path))
    tasks = [consumer_task, producer_task]

    # TODO Refactoring
    print(f"Connected: {websocket}, Path: {path}", file=sys.stderr)
    connections[path] = websocket
    print(f"Connections: {connections}", file=sys.stderr)
    print(json.dumps(objects, indent=2), file=sys.stderr)

    await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)


async def receiver(websocket, path):
    with open("console.log", "a") as f:
        async for message in websocket:
            print(message, flush=True)
            f.write(message + "\n")


async def sender(websocket, path):
    with open("console.log") as f:
        f.seek(0, 2)
        while True:
            await asyncio.sleep(0.01)
            for line in f:
                try:
                    info = json.loads(line)  # TODO jsonのパースのみチェックでいい？
                    # objects[info["name"]] = info

                    message = line
                    await websocket.send(message)
                except json.decoder.JSONDecodeError:
                    pass
                except websockets.ConnectionClosed:
                    print(f"Close Connection: ", connections["path"], file=sys.stderr)
                    # with open("console.log", "a") as f:
                    #     f.write(f"\n")


start_server = websockets.serve(handler, "0.0.0.0", PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
