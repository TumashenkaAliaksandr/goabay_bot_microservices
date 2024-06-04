import logging
import pika
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
# from telegram.ext import Filters
from django.conf import settings
import django
import asyncio

# Установка переменной окружения и инициализация Django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goabay_bot.settings')
django.setup()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def send_to_rabbitmq(message: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE)
    channel.basic_publish(exchange='', routing_key=settings.RABBITMQ_QUEUE, body=message)
    connection.close()

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет! Я ваш телеграм-бот.')

async def echo(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    send_to_rabbitmq(message)
    await update.message.reply_text('Ваше сообщение отправлено в очередь RabbitMQ.')

def main() -> None:
    application = Application.builder().token(settings.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(None, echo))  # Убираем фильтры для упрощения

    application.run_polling()

if __name__ == '__main__':
    main()
