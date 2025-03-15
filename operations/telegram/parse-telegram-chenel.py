from telethon import TelegramClient
import asyncio
import os
from dotenv import load_dotenv

# Загрузить переменные окружения из файла .env
load_dotenv()

# Замените эти значения на свои
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
channel_username = input('Введите имя канала (например, @my_channel): ')

# Создаем клиент
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start()

    # Получаем объект канала
    channel = await client.get_entity(channel_username)
    # Счетчик для строк и номер файла
    title = 'post'
    line_count = 0
    file_number = 1
    file_name = f'{title}_{file_number}.txt'

    # Получаем сообщения из канала
    async for message in client.iter_messages(channel):
        if message.text:  # Проверяем наличие текста и ссылки if message.text and 't.me' in message.text:
            print(message.text)  # Печатаем текст сообщения
            # Сохраняем в файл
            with open(file_name, 'a', encoding='utf-8') as f:
                f.write(message.text + '\n')

            line_count += 1

            if file_number == 5:
                break

                # Если достигли 2500 строк, создаем новый файл
            if line_count >= 500:
                file_number += 1
                file_name = f'{title}_{file_number}.txt'
                line_count = 0
# Запускаем асинхронную функцию
asyncio.run(main())