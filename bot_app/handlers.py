import aio_pika
import logging
from telegram.ext import CallbackContext
from telegram import Update
from goabay_bot import settings

# Глобальная переменная для хранения соединения
connection = None


async def get_connection():
    global connection
    if connection is None or connection.is_closed:
        connection = await aio_pika.connect_robust(host=settings.RABBITMQ_HOST)
    return connection


async def send_to_rabbitmq(message: str):
    try:
        conn = await get_connection()
        channel = await conn.channel()
        await channel.queue_declare(queue=settings.RABBITMQ_QUEUE)
        await channel.basic_publish(exchange='', routing_key=settings.RABBITMQ_QUEUE, body=message.encode())
        logging.info(f"Сообщение отправлено в RabbitMQ: {message}")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения в RabbitMQ: {str(e)}")


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет! Я ваш телеграм-бот.')


async def echo(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    await send_to_rabbitmq(message)
    await update.message.reply_text('Ваше сообщение отправлено в очередь RabbitMQ.')




# import aio_pika
# import pika
# from telegram.ext import CallbackContext
# from telegram import Update
# from goabay_bot import settings
#
#
# async def send_to_rabbitmq(message: str):
#     connection = await aio_pika.connect_robust(host=settings.RABBITMQ_HOST)
#     channel = await connection.channel()
#     await channel.queue_declare(queue=settings.RABBITMQ_QUEUE)
#     await channel.basic_publish(exchange='', routing_key=settings.RABBITMQ_QUEUE, body=message)
#     await connection.close()
#
#
# async def start(update: Update, context: CallbackContext) -> None:
#     await update.message.reply_text('Привет Я ваш телеграм-бот.')
#
#
# async def echo(update: Update, context: CallbackContext) -> None:
#     message = update.message.text
#     await send_to_rabbitmq(message)
#     await update.message.reply_text('Ваше сообщение отправлено в очередь RabbitMQ.')
