import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goabay_bot.settings')
django.setup()

from bot_app.templates.profile_date import profile_button_handler
import logging
import pika
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, filters
from django.conf import settings
from telegram.ext import CallbackQueryHandler
from bot_app.buttons_store import *
from bot_app.templates.registrations_store import store_registration_handler


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

    # Отправляем приветственное сообщение с кнопками
    await update.message.reply_text(welcome_message, reply_markup=main_markup)


async def echo(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    send_to_rabbitmq(message)
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
        await update.message.reply_text('Вы вернулись в "Главное меню 🍳".', reply_markup=main_markup)
    elif message == "Личный кабинет 👤":
        await store_registration_handler(update, context)
    if message == "✏️ Редактировать данные":
        # Запускаем новый процесс регистрации
        await store_registration_handler(update, context)
    elif message == "🔙 Назад в кабинет":
        await update.message.reply_text('Вы вернулись в кабинет.', reply_markup=profile_btn)


async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'edit_data':
        # Логика для исправления данных
        await query.edit_message_text("Пожалуйста, введите ваши данные снова.")
        # Возвращаем к началу процесса регистрации
        context.user_data['step'] = None  # Сброс шага регистрации
        await store_registration_handler(update, context)  # Начинаем процесс регистрации заново

    elif query.data == 'confirm_data':
        # Логика для подтверждения данных
        await query.edit_message_text("✔️ Ваши данные подтверждены!")
        # Отправляем сообщение с кнопками главного меню
        await query.message.reply_text('Главное меню: 🍳', reply_markup=profile_btn)
        # Очищаем данные пользователя
        context.user_data.clear()

    else:
        await query.edit_message_text("🤷‍♂️ Неизвестный выбор. Попробуйте снова.")


def main() -> None:
    application = Application.builder().token(settings.BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    # application.add_handler(MessageHandler(None, echo))  # Убираем фильтры для упрощения


    # Обработчик для регистрации в магазине
    store_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^(Личный кабинет 👤|✏️ Редактировать данные)$"), store_registration_handler)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_registration_handler)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_registration_handler)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_registration_handler)],
        },
        fallbacks=[],
    )

    application.add_handler(store_conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    # Обработчик для кнопки "👳‍♂️ Мои данные"
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("👳‍♂️ Мои данные"), profile_button_handler))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()


if __name__ == '__main__':
    main()