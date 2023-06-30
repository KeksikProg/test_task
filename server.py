import asyncio
import random
import logging
import datetime

# Переменные для настройки
SERVER_PORT = 8888
SERVER_IGNORE_CHANCE = 0.1
SERVER_RESPONSE_MIN = 0.1
SERVER_RESPONSE_MAX = 1.0
KEEPALIVE_INTERVAL = 5.0
RUNTIME = 300.0


# Инициализация логгера
logging.basicConfig(filename='server.log', level=logging.INFO,
                    format='%(message)s')


# Класс клиента
class Client:
    def __init__(self, num, writer):
        self.num = num
        self.writer = writer

    # Отправка сообщения клиенту
    async def send_message(self, message):
        self.writer.write(message.encode())
        await self.writer.drain()


# Класс сервера
class Server:
    def __init__(self):
        self.clients = []
        self.response_count = 0

    # Обработчик подключения нового клиента
    async def handle_client(self, reader, writer):
        client = Client(len(self.clients) + 1, writer)
        self.clients.append(client)

        while True: # Бесконечный цикл
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=3.0)
                date_tod = datetime.datetime.now().strftime("%Y-%m-%d")
                timestamp_get_request = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                message = data.decode().strip()
                if random.random() < SERVER_IGNORE_CHANCE:
                    logging.info(f'{date_tod};{timestamp_get_request};{message};(проигнорировано)')
                else:
                    delay = random.uniform(SERVER_RESPONSE_MIN, SERVER_RESPONSE_MAX)
                    await asyncio.sleep(delay)
                    response_count = self.response_count
                    response = f'[{response_count}/{(message.split()[0])[1:-1]}] PONG ({client.num})\n'.encode()
                    writer.write(response)
                    timestamp_answer = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    await writer.drain()
                    logging.info(f'{date_tod};{timestamp_get_request};{message};{timestamp_answer};{response.decode()[:-1]}')
                    self.response_count += 1
            except asyncio.TimeoutError:
                pass

    # Отправка сообщения клиентам
    async def send_message_to_clients(self, message):
        response_count = self.response_count
        response = f'[{response_count}] {message}\n'
        for client in self.clients:
            await client.send_message(response)
        self.response_count += 1

    # Отправда сообщения KEEPALIVE клиентам
    async def keepalive_loop(self):
        while True:
            await asyncio.sleep(KEEPALIVE_INTERVAL)
            await self.send_message_to_clients('keepalive')

    # Запуск сервера на заданное время
    async def run(self, runtime):
        self.server = await asyncio.start_server(self.handle_client, 'localhost', SERVER_PORT)
        asyncio.create_task(self.keepalive_loop())
        await asyncio.sleep(runtime)


# Запуск сервера
async def main():
    server = Server()
    await server.run(RUNTIME)

asyncio.run(main())
