#!/usr/bin/env python

# WS client example

import json
import asyncio
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
                print(f"< {price}: {side}: {size}: {block}")

asyncio.get_event_loop().run_until_complete(hello())