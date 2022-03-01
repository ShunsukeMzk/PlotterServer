import asyncio
import json
import websockets

# ---

async def stream():
    uri = 'ws://localhost:18080/kabusapi/websocket'

    async with websockets.connect(uri, ping_timeout=None) as ws:
        while not ws.closed:
            response = await ws.recv()
            board = json.loads(response)
            # print(json.dumps(board, indent=2))

            symbol = board["Symbol"]
            symbol_name = board["SymbolName"]
            current_price = board["CurrentPrice"]
            current_price_time = board["CurrentPriceTime"]
            print(f"{symbol} {symbol_name}: {current_price_time} {current_price}")

            # print("{} {} {}".format(
            #     board['Symbol'],
            #     board['SymbolName'],
            #     board['CurrentPrice'],@09898./
            # ))

loop = asyncio.get_event_loop()
loop.create_task(stream())
try:
    loop.run_forever()
except KeyboardInterrupt:
    exit()
