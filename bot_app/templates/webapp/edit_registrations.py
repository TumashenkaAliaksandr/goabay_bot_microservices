from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import CallbackContext

from bot_app.models import UserRegistration
from bot_app.templates.registrations_store import store_registration_handler


async def handle_edit_data(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id

    # Сброс шага регистрации и начало процесса регистрации заново
    registration, created = await sync_to_async(UserRegistration.objects.get_or_create)(user_id=user_id)
    registration.step = None  # Сбрасываем шаг регистрации
    await sync_to_async(registration.save)()  # Сохраняем изменения асинхронно

    # Перенаправляем пользователя в начало процесса регистрации
    await update.message.reply_text(
        "***Для того чтобы делать покупки в магазине 🏪 GoaBay***\n"
        "***Нужно пройти 📜 РЕГИСТРАЦИЮ***\n\n"
        "_Пожалуйста, ✍️ введите ваше имя:_",
        parse_mode='MarkdownV2'
    )
    # Запускаем новый процесс регистрации
    return await store_registration_handler(update, context)
