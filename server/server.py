#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
import datetime
import random
import websockets
import os

PORT = os.getenv("PORT")

async def handler(websocket, path):
    consumer_task = asyncio.ensure_future(reciever(websocket, path))
    produser_task = asyncio.ensure_future(sender(websocket, path))
    tasks = [consumer_task, produser_task]
    await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)


async def reciever(websocket, path):
    async for message in websocket:
        print(message)


async def sender(websocket, path):
    with open("console.log") as f:
        f.seek(0, 2)
        while True:
            await asyncio.sleep(0.01)
            for line in f:
                try:
                    if line in ("\n", "clear\n"):
                        message = "clear"
                    elif line.startswith("color"):
                        message = line.strip()
                    else:
                        if "," in line:
                            x, y, z, *_ = line.strip().split(",")
                        else:
                            x, y, z, *_ = line.strip().split()
                        x = float(x)
                        y = float(y)
                        z = float(z)
                        message = f"{x} {y} {z}"
                except Exception:
                    pass
                else:
                    await websocket.send(message)


start_server = websockets.serve(handler, "0.0.0.0", PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
