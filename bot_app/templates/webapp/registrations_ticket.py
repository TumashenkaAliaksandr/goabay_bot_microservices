# registration.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from bot_app.buttons_store import main_markup


async def ticket_registration_handler(update: Update, context: CallbackContext) -> int:
    step = context.user_data.get('step')
    user_data = context.user_data.get('registration', {})

    if step is None:
        # Начало процесса регистрации
        await update.message.reply_text("Пожалуйста, введите ваше имя:")
        context.user_data['step'] = 'name'
        context.user_data['registration'] = {'user_id': update.message.from_user.id}
        return 1  # NAME

    elif step == 'name':
        # Сохраняем имя пользователя и просим ввести email
        user_data['name'] = update.message.text
        await update.message.reply_text("Спасибо! Теперь введите ваш email:")
        context.user_data['step'] = 'email'
        return 2  # EMAIL

    elif step == 'email':
        # Сохраняем email и просим ввести телефон
        user_data['email'] = update.message.text
        await update.message.reply_text("Отлично! Теперь введите ваш телефонный номер:")
        context.user_data['step'] = 'phone'
        return 3  # PHONE

    elif step == 'phone':
        # Сохраняем телефон и завершаем регистрацию
        user_data['phone'] = update.message.text
        await update.message.reply_text("Регистрация завершена! Спасибо!")

        # Отправляем сообщение с кнопками главного меню
        await update.message.reply_text('Вы вернулись в главное меню:', reply_markup=main_markup)

        context.user_data.clear()
        return ConversationHandler.END

    else:
        # Ошибка, если шаг не распознан
        await update.message.reply_text("Что-то пошло не так. Попробуйте снова.")
        return ConversationHandler.END
