import os

import django

from bot_app.templates.webapp.answers.answer_money import get_currency_rates
from bot_app.templates.webapp.buttons.buttons import reply_markup_pay, back_button_go
from bot_app.templates.webapp.buttons.buttons_how_working import goa_pay_btn
from bot_app.templates.webapp.text_files.info_pay import payment_info

# Настройка окружения и Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goabay_bot.settings')
django.setup()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, filters
from telegram.ext import CallbackQueryHandler
from django.conf import settings
from bot_app.templates.profile_date import profile_button_handler
from bot_app.templates.webapp.buttons.buttons_store import *
from bot_app.templates.registrations_store import store_registration_handler
import logging
import pika


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Отправка сообщений в RabbitMQ
def send_to_rabbitmq(message: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE)
    channel.basic_publish(exchange='', routing_key=settings.RABBITMQ_QUEUE, body=message)
    connection.close()


# Обработка команды /start
async def start(update: Update, context: CallbackContext) -> None:
    with open('welcome.txt', 'r', encoding='utf-8') as file:
        welcome_message = file.read()

    await update.message.reply_text(welcome_message, reply_markup=main_markup)


# Основная функция для обработки сообщений
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
    elif message == "💳 Оплата":
        await update.message.reply_text('👳‍♂️ Оплата индийских товаров и услуг', reply_markup=goa_pay_btn)
    elif message == "⬅️ Назад":
        await update.message.reply_text('Вы вернулись в "Главное меню 🍳".', reply_markup=main_markup)
    elif message == "⬅️ Назад к информации":
        await update.message.reply_text('Вы вернулись в "Как мы работаем ⌚️".', reply_markup=how_we_work_btn)

    if message == "Способы оплаты 💵":
        await update.message.reply_text('Способы оплаты 💵', reply_markup=reply_markup_pay)
        # Путь к вашему текстовому файлу
        # text_file_path = 'templates/webapp/text_files/payment_methods.py'
        # photo_path = 'static/webapp/img/bank-transfer-logo-min.png'  # Замените на путь к вашему изображению
        #
        # # Проверка существования файла
        # if not os.path.isfile(text_file_path):
        #     await update.message.reply_text("Файл с информацией не найден.")
        # else:
        #     try:
        #         # Чтение текстового файла
        #         with open(text_file_path, 'r', encoding='utf-8') as file:
        #             html_content = file.read()
        #
        #             # Текст для подписи
        #             caption = html_content[:1024]
        #
        #         await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(photo_path, 'rb'),
        #                                      caption=caption, parse_mode='Markdown')
        #
        #     except Exception as e:
        #         await update.message.reply_text(f"Произошла ошибка при чтении файла: {e}")

    elif message == "Как мы работаем ⌛️️":
        await update.message.reply_text('Вы выбрали "Как мы работаем ⌛️️".', reply_markup=how_we_work_btn)

    if message == '💸 Курс валют':
        await get_currency_rates(update, context)


    # if message == "Личный кабинет 👤":
    #     # Проверяем регистрацию и вызываем соответствующий обработчик
    #     user_id = update.message.from_user.id
    #     registration = await sync_to_async(UserRegistration.objects.filter)(user_id=user_id).first()
    #
    #     if registration and registration.name and registration.email and registration.phone:
    #         # Пользователь зарегистрирован, показываем личный кабинет
    #         await show_user_info(update, context)
    #     else:
    #         # Пользователь не зарегистрирован, запускаем регистрацию
    #         await store_registration_handler(update, context)
    #
    # elif message == "✏️ Редактировать данные":
    #     await store_registration_handler(update, context)

    elif message == "🔙 Назад в кабинет":
        await update.message.reply_text('Вы вернулись в кабинет 👤', reply_markup=profile_btn)


# Обработка инлайн-кнопок
async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'edit_data':
        await query.edit_message_text("✏️ Пожалуйста, введите ваши данные снова.")
        context.user_data['step'] = None  # Сброс шага регистрации
        await store_registration_handler(update, context)  # Начинаем процесс регистрации заново
    elif query.data == 'confirm_data':
        await query.edit_message_text("✔️ Ваши данные подтверждены!")
        await query.edit_message_text('Главное меню: 🍳', reply_markup=profile_btn)
        context.user_data.clear()

    # Получение текста в зависимости от нажатой кнопки
    payment_method = query.data
    if payment_method in payment_info:
        await query.edit_message_text(payment_info[payment_method], reply_markup=back_button_go)

    elif payment_method == 'back_pay':
        await query.edit_message_text("👇 💵 Выберите способ оплаты:", reply_markup=reply_markup_pay)

    else:
        await query.edit_message_text("🤷‍♂️ Неизвестный выбор. Попробуйте снова.")


# Основная функция для запуска бота
def main() -> None:
    application = Application.builder().token(settings.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    # ConversationHandler для регистрации в магазине
    store_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & filters.Regex("^(Личный кабинет 👤)$"), store_registration_handler),
            MessageHandler(filters.TEXT & filters.Regex("^(✏️ Редактировать данные)$"), store_registration_handler)
        ],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_registration_handler)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_registration_handler)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_registration_handler)],
        },
        fallbacks=[],
    )

    application.add_handler(store_conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("👳‍♂️ Мои данные"), profile_button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()


if __name__ == '__main__':
    main()
