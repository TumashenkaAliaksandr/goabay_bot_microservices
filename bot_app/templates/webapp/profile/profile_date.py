import os
import django
from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import CallbackContext
from bot_app.templates.webapp.buttons.buttons_store import main_markup, change_profile_btn

# Установка переменной окружения и инициализация Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goabay_bot.settings')
django.setup()

from bot_app.models import UserRegistration  # Import Django models here


async def show_user_info(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    # Получаем данные пользователя
    registration = await sync_to_async(UserRegistration.objects.get)(user_id=user_id)

    user_info = (f"👳‍♂️ Ваши данные:\n"
                 f"Имя: {registration.name}\n"
                 f"Email: {registration.email}\n"
                 f"Телефон: {registration.phone}\n\n"
                 "Выберите, что хотите сделать:")

    # Отправляем сообщение с данными пользователя и меню
    await update.message.reply_text(user_info, parse_mode='MarkdownV2', reply_markup=change_profile_btn)


# Обработчик для кнопки "👳‍♂️ Мои данные"
async def profile_button_handler(update: Update, context: CallbackContext) -> None:
    message = update.message.text

    if message == "👳‍♂️ Мои данные":
        await show_user_info(update, context)  # Показываем данные пользователя
    else:
        await update.message.reply_text('Неизвестная команда.', reply_markup=main_markup)
