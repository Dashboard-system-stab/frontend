import asyncio
import pandas as pd

GATEWAY_ADDR = "127.0.0.1"
GATEWAY_PORT = 9999
DATA_FILE = "weather_data.csv"


class ClientProtocol(asyncio.DatagramProtocol):
    def error_received(self, exc):
        print(f"[!] Системная ошибка сети: {exc}")

async def send_data(filepath):
    loop = asyncio.get_running_loop()

    df = pd.read_csv(filepath)
    
    data = df.to_json(orient='records', lines=True).splitlines()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: ClientProtocol(),
        remote_addr=(GATEWAY_ADDR, GATEWAY_PORT)
    )

    try:
        for json_str in data:
            payload = json_str.encode('utf-8')
            
            transport.sendto(payload)
            print(f"[UDP] Отправлен пакет: {json_str}")
            
            await asyncio.sleep(0.5)

        print("[*] Все данные из датафрейма успешно отправлены!")
        print("[*] Начинаю передачу сначала файла\n")
    finally:

        transport.close()

async def main():
    try:
        while True:    
            await send_data(DATA_FILE)
    except FileNotFoundError:
        print("[!] Ошибка: Файл csv не найден.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!!!] Клиент прерван пользователем.")
