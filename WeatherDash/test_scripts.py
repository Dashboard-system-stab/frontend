# ivan_test.py
import asyncio
import websockets
import json
import os

IVAN_PORT = 7777

# Тестовые скрипты — создадим их при запуске
TEST_SCRIPTS = {
    "script1.py": "def calculate(data):\n    return sum(data) / len(data)\n",
    "script2.py": "def process(data):\n    return [x * 2 for x in data]\n",
    "script3.py": "def rms(data):\n    return (sum(x**2 for x in data) / len(data)) ** 0.5\n",
}

# Создаём тестовые файлы при запуске
for filename, content in TEST_SCRIPTS.items():
    with open(filename, 'w') as f:
        f.write(content)
print("[*] Тестовые файлы созданы: script1.py, script2.py, script3.py")


async def handler(websocket):
    print("[WS] Владислав подключился")
    async for message in websocket:
        try:
            data = json.loads(message)
            msg_type = data.get('type')

            # Список файлов
            if msg_type == 'get_list':
                files = [f for f in os.listdir('.') if f.endswith('.py') and f.startswith('script')]
                response = json.dumps({'files': files})
                await websocket.send(response)
                print(f"[*] Отправлен список файлов: {files}")

            # Чтение файла
            elif msg_type == 'get_file':
                filename = data.get('filename')
                with open(filename, 'r') as f:
                    content = f.read()
                response = json.dumps({'filename': filename, 'content': content})
                await websocket.send(response)
                print(f"[*] Отправлено содержимое файла: {filename}")

            # Сохранение файла
            elif msg_type == 'save_file':
                filename = data.get('filename')
                content = data.get('content')
                with open(filename, 'w') as f:
                    f.write(content)
                response = json.dumps({'status': 'ok'})
                await websocket.send(response)
                print(f"[*] Файл сохранён: {filename}")

        except Exception as e:
            print(f"[!] Ошибка: {e}")


async def main():
    async with websockets.serve(handler, 'localhost', IVAN_PORT):
        print(f"[*] Тестовый сервер Ивана запущен на порту {IVAN_PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Сервер остановлен.")
