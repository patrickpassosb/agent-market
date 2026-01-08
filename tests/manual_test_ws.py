import asyncio
import websockets
import json
import sys

async def test():
    uri = "ws://localhost:8000/ws"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WS")
            msg = await websocket.recv()
            data = json.loads(msg)
            print(f"Received update for tick: {data.get('tick')}")
            if "news" in data:
                print(f"News present: {data['news'] is not None}")
    except Exception as e:
        print(f"WS Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test())
