#!/usr/bin/env python

# WS client example

import sys
import json
import yaml
import asyncio
from datetime import datetime
import websockets

import numpy as np


z = 1

uri = "wss://ws.lightstream.bitflyer.com/json-rpc"
# product = "FX_BTC_JPY"
product = "BTC_JPY"

base = {"price": None, "time": None}

base_time = datetime.now().timestamp()

objects = []

_print = print


def custom_print(*args, **kwargs):
    _print(flush=True, *args, **kwargs)


print = custom_print


def adjust_price(price):
    if base["price"]:
        return (price - base["price"]) / 1_000


def adjust_size(size):
    # return np.log2(size * 40)
    return size * 10


async def handler():
    order_book_task = asyncio.ensure_future(order_book())
    executions_task = asyncio.ensure_future(executions())
    management_task = asyncio.ensure_future(management())
    # tasks = [order_book_task, executions_task]
    # tasks = [executions_task]
    #
    # await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)


async def management():
    while True:
        await asyncio.sleep(0.05)
        if base["price"] is None:
            continue

        distance = base_time - datetime.now().timestamp()
        translate_info = {
            "name": f"order",
            "type": "--",
            "position": {"x": 0, "y": 0, "z": distance},
            "scale": {"x": 1, "y": 1, "z": 1}
        }
        print(json.dumps(translate_info))

        for obj in objects[:-100_000]:
            delete_info = {
                "name": obj["name"],
                "type": "__DELETE__"
            }
            print(json.dumps(delete_info))
        del objects[:-100_000]


async def executions():
    channel = f"lightning_executions_{product}"
    async with websockets.connect(uri) as websocket:
        subscribe = json.dumps({"method": "subscribe", "params": {"channel": channel}})

        await websocket.send(subscribe)
        print(f"> {subscribe}", file=sys.stderr)

        while True:
            message = await websocket.recv()
            message = json.loads(message)

            message = message["params"]["message"]

            if base["price"] is None:
                continue

            for execution in message:
                # time = datetime.strptime(execution["exec_date"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp() - base_time
                exec_date = execution["exec_date"]
                exec_date = exec_date.replace("Z", "")
                exec_date = (exec_date + "000000")[:26] + "+00:00"

                time = datetime.fromisoformat(exec_date).timestamp() - base_time

                price = adjust_price(execution["price"])

                size = execution["size"]
                size = adjust_size(size)

                side = execution["side"]

                if side == "BUY":
                    position = size / 2
                    color = {"r": 0.54, "g": 0.32, "b": 0.63, "a": 1}  # 紫 139,82,161
                else:  # side: SELL
                    position = - size / 2
                    color = {"r": 0, "g": 0.5, "b": 0, "a": 1}  # 緑 0,128,0
                execution_info = {
                    "name": f"order/exec/{time}-{price}",
                    "type": "Object/Cube",
                    "position": {"x": position, "y": price, "z": time},
                    "rotation": {"x": 0, "y": 0, "z": 0},
                    "scale": {"x": size, "y": 0.1, "z": 0.1},
                    "color": color,
                }
                print(json.dumps(execution_info))
                objects.append(execution_info)
                # print(execution["exec_date"], execution["price"], execution["size"], execution["side"], sep="\t")


async def order_book():
    # channel = "lightning_board_FX_BTC_JPY"
    channel = f"lightning_board_snapshot_{product}"
    async with websockets.connect(uri) as websocket:
        subscribe = json.dumps({"method": "subscribe", "params": {"channel": channel}})

        await websocket.send(subscribe)
        print(f"> {subscribe}", file=sys.stderr)

        previous_mid_price = None
        previous_time = None

        while True:
            message = await websocket.recv()
            message = json.loads(message)

            message = message["params"]["message"]
            mid_price = message["mid_price"]
            time = datetime.now().timestamp() - base_time

            if base["price"] is None:
                base["price"] = mid_price

            mid_price = adjust_price(mid_price)

            if previous_mid_price and mid_price > previous_mid_price:
                point_color = {"r": 1, "g": 1, "b": 1, "a": 1}
            else:
                point_color = {"r": 0, "g": 0, "b": 0, "a": 1}

            mid_price_info = {
                "name": f"order/mid_price/{time}",
                "type": "Object/Sphere",
                "position": {"x": 0, "y": mid_price, "z": time},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 0.1, "y": 0.1, "z": 0.1},
                "color": point_color,
            }
            print(json.dumps(mid_price_info))

            if previous_mid_price is not None:
                line_info = {
                    "name": f"order/mid_price/{previous_time}_{time}",
                    "type": "Object/Line"
                }
                print(json.dumps(line_info))
                objects.append(line_info)

            previous_mid_price = mid_price
            previous_time = time

            for j, ask in enumerate(filter(lambda x: x["size"], message["asks"])):
                if j == 20:
                    break
                price, size = ask.values()
                price = adjust_price(price)
                size = adjust_size(size)
                ask_info = {
                    "name": f"order/ask/{time}-{j}",
                    "type": "Object/Cube",
                    "position": {"x": -size / 2, "y": price, "z": time},
                    "rotation": {"x": 0, "y": 0, "z": 0},
                    "scale": {"x": size, "y": 0.1, "z": 0.1},
                    "color": {"r": 1, "g": 0, "b": 0, "a": 1},
                }
                print(json.dumps(ask_info))
                objects.append(ask_info)

            for j, bid in enumerate(filter(lambda x: x["size"], message["bids"])):
                if j == 20:
                    break
                price, size = bid.values()
                price = adjust_price(price)
                size = adjust_size(size)
                bid_info = {
                    "name": f"order/bid/{time}-{j}",
                    "type": "Object/Cube",
                    "position": {"x": size / 2, "y": price, "z": time},
                    "rotation": {"x": 0, "y": 0, "z": 0},
                    "scale": {"x": size, "y": 0.1, "z": 0.1},
                    "color": {"r": 1, "g": 1, "b": 0, "a": 1},
                }
                print(json.dumps(bid_info))
                objects.append(bid_info)


asyncio.get_event_loop().run_until_complete(handler())
asyncio.get_event_loop().run_forever()
