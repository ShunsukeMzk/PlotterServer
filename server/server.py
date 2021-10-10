#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
import datetime
import random
import websockets
import os
import json

PORT = os.getenv("PORT")

async def handler(websocket, path):
    consumer_task = asyncio.ensure_future(reciever(websocket, path))
    produser_task = asyncio.ensure_future(sender(websocket, path))
    tasks = [consumer_task, produser_task]
    await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)


async def reciever(websocket, path):
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
                    _ = json.loads(line)  # TODO jsonのパースのみチェックでいい？
                    message = line
                except Exception:
                    pass
                else:
                    await websocket.send(message)


start_server = websockets.serve(handler, "0.0.0.0", PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
