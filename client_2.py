# Скрипт для запуска клиента 2
import asyncio
import logging
import random
import datetime

CLIENT_INTERVAL_MIN = 0.3
CLIENT_INTERVAL_MAX = 3.0

logging.basicConfig(filename='client_2.log', level=logging.INFO, format='%(message)s')


async def main():
    reader, writer = await asyncio.open_connection('localhost', 8888)
    message_count = 0
    while True:
        date_tod = datetime.datetime.now().strftime("%Y-%m-%d")
        delay = random.uniform(CLIENT_INTERVAL_MIN, CLIENT_INTERVAL_MAX)
        await asyncio.sleep(delay)
        message_count += 1
        message = f'[{message_count}] PING\n'
        writer.write(message.encode())
        await writer.drain()
        timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]

        try:
            data = await asyncio.wait_for(reader.readline(), timeout=2.0)
            timestamp_get_answer = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
            data = data.decode()
            if data.split()[1] == 'keepalive':
                logging.info(f'{date_tod};;;{timestamp_get_answer};{data[:-1]}')
            else:
                logging.info(f'{date_tod};{timestamp};{message[:-1]};{timestamp_get_answer};{data[:-1]}')
        except asyncio.TimeoutError:  # Если инфа не пришла
            timestamp_get_answer = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
            logging.info(f'{date_tod};{timestamp};{message[:-1]};{timestamp_get_answer};(timeout)')

asyncio.run(main())
