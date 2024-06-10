import aio_pika
import pika
from telegram.ext import CallbackContext
from telegram import Update
from goabay_bot import settings

async def send_to_rabbitmq(message: str):
    connection = await aio_pika.connect_robust(host=settings.RABBITMQ_HOST)
    channel = await connection.channel()
    await channel.queue_declare(queue=settings.RABBITMQ_QUEUE)
    await channel.basic_publish(exchange='', routing_key=settings.RABBITMQ_QUEUE, body=message)
    await connection.close()

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет Я ваш телеграм-бот.')

async def echo(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    await send_to_rabbitmq(message)
    await update.message.reply_text('Ваше сообщение отправлено в очередь RabbitMQ.')
