# main.py
import logging
import pika
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from django.conf import settings
import django
import asyncio
from buttons import *

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


# Функция для обработки команды /start
async def start(update: Update, context: CallbackContext) -> None:
    # Читаем сообщение приветствия из файла
    with open('welcome.txt', 'r', encoding='utf-8') as file:
        welcome_message = file.read()

    # Создаем кнопки "Регистрация на рейс" и "Магазин"
    start_buttons = [['✍️ Регистрация на рейс', '🏪 Магазин']]
    main_markup = ReplyKeyboardMarkup(start_buttons, resize_keyboard=True, one_time_keyboard=True)

    # Отправляем приветственное сообщение с кнопками
    await update.message.reply_text(welcome_message, reply_markup=main_markup)


async def echo(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    send_to_rabbitmq(message)
    if message == "✍️ Регистрация на рейс":
        await update.message.reply_text('Вы выбрали "✍️ Регистрация на рейс".', reply_markup=main_markup)
    if message == "🏪 Магазин":
        await update.message.reply_text('Вы выбрали "🏪 Магазин".', reply_markup=main_markup)
    if message == "Товары из Индии 👳‍♀️":
        await update.message.reply_text('Вы выбрали "Товары из Индии 👳‍♀️".', reply_markup=products_btn_india)
    elif message == "Как мы работаем ⌚️":
        await update.message.reply_text('Вы выбрали "Как мы работаем ⌚️".', reply_markup=how_we_work_btn)
    elif message == "Сервис 🔧":
        await update.message.reply_text('Вы выбрали "Сервис 🔧".', reply_markup=service_btn)
    elif message == "О компании 🏢":
        await update.message.reply_text('Вы выбрали "О компании 🏢".', reply_markup=about_btn)
    elif message == "Наш Блог 📚":
        await update.message.reply_text('Вы выбрали "Наш Блог 📚".', reply_markup=blog_btn)
    elif message == "⬅️ Назад":
        await update.message.reply_text('Вы опали в "Главное меню 📖".', reply_markup=main_markup)
    elif message == "Личный кабинет 👤":
        await update.message.reply_text('Вы опали в "Личный кабинет 👤".', reply_markup=profile_btn)


def main() -> None:
    application = Application.builder().token(settings.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(None, echo))  # Убираем фильтры для упрощения

    application.run_polling()


if __name__ == '__main__':
    main()
