import asyncio
import websockets
import json

async def handler(websocket):
    async for message in websocket:
        try:
            data = json.loads(message)
            x = data['x']
            y = data['y']
            result = x * y  # любая обработка
            await websocket.send(json.dumps({'result': result}))
        except Exception as e:
            await websocket.send(json.dumps({'error': str(e)}))

async def main():
    async with websockets.serve(handler, 'localhost', 8765):
        print("WS сервер запущен на ws://localhost:8765")
        await asyncio.Future()

asyncio.run(main())