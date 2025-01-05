from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from bot_app.models import UserRegistration
from asgiref.sync import sync_to_async
from bot_app.templates.webapp.profile.profile_date import show_user_info

# Константы для состояний ConversationHandler
STEP_REGISTER_NAME = 1
STEP_EDIT_NAME = 2


# Асинхронный обработчик кнопок личного кабинета
async def store_registration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    message_text = update.message.text

    try:
        print(f"Обработка сообщения '{message_text}' от пользователя {user_id}.")  # Логируем запрос

        # Получаем регистрацию пользователя асинхронно
        registrations = await sync_to_async(list)(UserRegistration.objects.filter(user_id=user_id))

        if message_text == "Личный кабинет 👤":
            if registrations:
                registration = registrations[0]
                if registration.is_registered:
                    await show_user_info(update, context)  # Отображаем данные пользователя
                    return ConversationHandler.END
            else:
                keyboard = [
                    [InlineKeyboardButton("Начать регистрацию", callback_data="start_registration")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    "Вы не зарегистрированы. Пожалуйста, пройдите регистрацию.",
                    reply_markup=reply_markup,
                )
                return ConversationHandler.END

        elif message_text == "✏️ Редактировать данные":
            if not registrations:
                await update.message.reply_text("Сначала вам нужно зарегистрироваться.")
                return ConversationHandler.END

            context.user_data["step"] = "edit_name"
            await update.message.reply_text("Пожалуйста, введите ваше новое имя:")
            return STEP_EDIT_NAME

    except Exception as e:
        print(f"Ошибка в store_registration_handler: {e}")  # Логируем ошибку
        await update.message.reply_text("Что-то пошло не так. Попробуйте снова.")
        return ConversationHandler.END


# Асинхронный обработчик нажатия на кнопку "Начать регистрацию"
async def start_registration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()  # Обязательно отвечаем на callback, чтобы убрать "часики"

    print(f"Пользователь {user_id} начал регистрацию.")  # Логируем событие
    await query.edit_message_text("Регистрация началась! Пожалуйста, введите ваше имя.")
    context.user_data["step"] = "register_name"
    return STEP_REGISTER_NAME


# Асинхронный обработчик ввода имени
async def register_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    name = update.message.text

    try:
        print(f"Пользователь {user_id} ввел имя: {name}.")  # Логируем данные

        # Сохраняем имя в базу данных
        await sync_to_async(UserRegistration.objects.update_or_create)(
            user_id=user_id, defaults={"name": name, "is_registered": True}
        )

        await update.message.reply_text(
            "Спасибо! Ваше имя сохранено. Регистрация завершена."
        )
        return ConversationHandler.END

    except Exception as e:
        print(f"Ошибка в register_name_handler: {e}")  # Логируем ошибку
        await update.message.reply_text("Произошла ошибка. Попробуйте снова.")
        return ConversationHandler.END
