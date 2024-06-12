# main.py
import logging
import pika
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from django.conf import settings
import django
import asyncio
from buttons import markup, inline_markup_india, inline_markup_how_we_work, inline_markup_service, inline_markup_about, inline_markup_blog

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
    await update.message.reply_text('Привет Я ваш телеграм-бот.', reply_markup=markup)

async def echo(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    send_to_rabbitmq(message)
    if message == "Товары из Индии 👳‍♀️":
        await update.message.reply_text('Вы выбрали "Товары из Индии 👳‍♀️".', reply_markup=inline_markup_india)
    elif message == "Как мы работаем ⌚️":
        await update.message.reply_text('Вы выбрали "Как мы работаем ⌚️".', reply_markup=inline_markup_how_we_work)
    elif message == "Сервис 🔧":
        await update.message.reply_text('Вы выбрали "Сервис 🔧".', reply_markup=inline_markup_service)
    elif message == "О компании 🏢":
        await update.message.reply_text('Вы выбрали "О компании 🏢".', reply_markup=inline_markup_about)
    elif message == "Наш Блог 📚":
        await update.message.reply_text('Вы выбрали "Наш Блог 📚".', reply_markup=inline_markup_blog)

def main() -> None:
    application = Application.builder().token(settings.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(None, echo))  # Убираем фильтры для упрощения

    application.run_polling()

if __name__ == '__main__':
    main()
