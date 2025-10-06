import asyncio

import websockets

BINANCE_WS_URL = "wss://fstream.binance.com"


async def listen_aggtrade():
    url = f"{BINANCE_WS_URL}/stream?streams=btcusdt@aggTrade/ethusdt@aggTrade/bnbusdt@aggTrade"
    async with websockets.connect(url) as ws:
        async for message in ws:
            print(f"Received message: {message}")


if __name__ == "__main__":
    asyncio.run(listen_aggtrade())
