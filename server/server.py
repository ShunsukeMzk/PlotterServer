#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
import datetime
import random
import websockets
import os

PORT = os.getenv("PORT")


async def time(websocket, path):
    with open("console.log") as f:
        f.seek(0, 2)
        while True:
            await asyncio.sleep(0.01)
            for line in f:
                try:
                    if line in ("\n", "clear\n"):
                        message = "clear"
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

            # now = datetime.datetime.utcnow().isoformat() + "Z"
            # await websocket.send(now)
            # await asyncio.sleep(random.random() * 3)
            # line = f.readline()  # TODO 入力待ち処理
            # if line:
            #     await websocket.send(line)

start_server = websockets.serve(time, "0.0.0.0", PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
