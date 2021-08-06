#!/usr/bin/env python

# WS client example

import json
import asyncio
import websockets

channel = "lightning_executions_FX_BTC_JPY"

print("date", "price", "size", "side", sep="\t")
async def hello():
    uri = "wss://ws.lightstream.bitflyer.com/json-rpc"
    async with websockets.connect(uri) as websocket:
        subscribe = json.dumps(
            {'method': 'subscribe',
             'params': {'channel': channel}
             }
        )

        await websocket.send(subscribe)
        # print(f"> {subscribe}")

        while True:
            message = await websocket.recv()
            message = json.loads(message)
            executions = message["params"]["message"]
            for execution in executions:
                date = execution["exec_date"]
                price = execution["price"]
                side = execution["side"]
                mark = "+" if side == "BUY" else "-"
                size = execution["size"]
                block = mark * (int(size * 1000))
                # print(f"< {price}: {side}: {size}: {block}")
                print(date, price, size, side, sep="\t")

asyncio.get_event_loop().run_until_complete(hello())