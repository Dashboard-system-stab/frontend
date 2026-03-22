import asyncio
import websockets
import json

BACKEND_ADDR = "127.0.0.1"
BACKEND_PORT = 8888
WEBSOCKET_PORT = 8765

coefficients = {"x": 1.0, "y": 1.0}
frontend_clients = set()


class GatewayProtocol(asyncio.Protocol):
    def __init__(self):
        self.buffer = ""

    def data_received(self, data):
        try:
            self.buffer += data.decode('utf-8')
            lines = self.buffer.split('\n')
            self.buffer = lines[-1]

            for line in lines[:-1]:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                record['temperature'] = record['temperature'] * coefficients['x'] * coefficients['y']
                print(f"[TCP] Получено от шлюза, отправляю Владиславу: {record}")
                asyncio.create_task(send_to_frontends(record))

            if self.buffer.strip():
                try:
                    record = json.loads(self.buffer.strip())
                    self.buffer = ""
                    record['temperature'] = record['temperature'] * coefficients['x'] * coefficients['y']
                    print(f"[TCP] Получено от шлюза, отправляю Владиславу: {record}")
                    asyncio.create_task(send_to_frontends(record))
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            print(f"[!] Ошибка обработки данных: {e}")


async def send_to_frontends(record):
    for client in frontend_clients.copy():
        try:
            await client.send(json.dumps(record))
        except Exception:
            frontend_clients.discard(client)


async def handle_frontend(websocket):
    frontend_clients.add(websocket)
    print("[WS] Владислав подключился")
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "coefficients":
                coefficients["x"] = data["x"]
                coefficients["y"] = data["y"]
                print(f"[WS] Получены коэффициенты: x={data['x']}, y={data['y']}")
    finally:
        frontend_clients.discard(websocket)
        print("[WS] Владислав отключился")


async def main():
    loop = asyncio.get_running_loop()

    tcp_server = await loop.create_server(
        lambda: GatewayProtocol(),
        BACKEND_ADDR,
        BACKEND_PORT
    )

    ws_server = await websockets.serve(handle_frontend, "localhost", WEBSOCKET_PORT)

    print(f"[*] TCP сервер запущен на порту {BACKEND_PORT} (от шлюза)")
    print(f"[*] WebSocket сервер запущен на порту {WEBSOCKET_PORT} (от Владислава)")

    async with tcp_server:
        async with ws_server:
            await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Роман остановлен.")