#!/usr/bin/env python

# WS client example

import json
import asyncio
import datetime
import websockets

channel = "lightning_executions_BTC_JPY"


async def hello():
    uri = "wss://ws.lightstream.bitflyer.com/json-rpc"
    async with websockets.connect(uri) as websocket:
        subscribe = json.dumps(
            {'method': 'subscribe',
             'params': {'channel': channel}
             }
        )

        await websocket.send(subscribe)
        print(f"> {subscribe}")

        base_price = None
        base_time = None

        while True:
            message = await websocket.recv()
            message = json.loads(message)
            executions = message["params"]["message"]
            for execution in executions:
                price = execution["price"]
                side = execution["side"]
                mark = "+" if side == "BUY" else "-"
                size = execution["size"]
                block = mark * (int(size * 1000))
                now = datetime.datetime.now()

                if base_price is None:
                    base_time = now
                
                if base_price is None:
                    base_price = price

                x = (now - base_time).seconds / 10
                y = (price - base_price) / 1_000
                z = 0  # 固定

                if side == "BUY":
                    print("color:red", flush=True)
                else:
                    print("color:blue", flush=True)
                print(x, y, z, sep="\t", flush=True)

asyncio.get_event_loop().run_until_complete(hello())