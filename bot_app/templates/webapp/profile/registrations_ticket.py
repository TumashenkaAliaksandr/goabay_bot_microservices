# registration.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from bot_app.models import UserRegistration  # Импортируем модель UserRegistration
from asgiref.sync import sync_to_async


async def ticket_registration_handler(update: Update, context: CallbackContext) -> int:
    step = context.user_data.get('step')
    user_id = update.message.from_user.id

    print(f"Начало обработки регистрации для пользователя: {user_id}")  # Отладка

    try:
        # Начало процесса регистрации
        if step is None:
            print("Шаг не установлен. Запрашиваем имя пользователя.")  # Отладка
            await update.message.reply_text("Пожалуйста, введите ваше имя:")
            context.user_data['step'] = 'edit_name'  # Устанавливаем шаг редактирования
            return 1  # Переход к шагу редактирования имени

        # Обработка шагов редактирования
        if step == 'edit_name':
            print(f"Получено имя: {update.message.text}")  # Отладка

            # Создаем новую запись для пользователя
            registration = UserRegistration(user_id=user_id)
            registration.name = update.message.text

            await sync_to_async(registration.save)()
            print(f"Имя сохранено: {registration.name}")  # Отладка

            await update.message.reply_text("Спасибо! Теперь введите ваш email:")
            context.user_data['step'] = 'edit_email'
            return 2  # Переход к шагу редактирования email

        elif step == 'edit_email':
            registration = await sync_to_async(UserRegistration.objects.filter)(user_id=user_id).first()
            if registration is None:
                await update.message.reply_text("Ошибка: регистрация не была завершена. Пожалуйста, начните заново.")
                return ConversationHandler.END

            print(f"Получен email: {update.message.text}")  # Отладка

            registration.email = update.message.text
            await sync_to_async(registration.save)()
            print(f"Email сохранен: {registration.email}")  # Отладка

            await update.message.reply_text("Отлично! Теперь введите ваш телефонный номер:")
            context.user_data['step'] = 'edit_phone'
            return 3  # Переход к шагу редактирования телефона

        elif step == 'edit_phone':
            registration = await sync_to_async(UserRegistration.objects.filter)(user_id=user_id).first()
            if registration is None:
                await update.message.reply_text("Ошибка: регистрация не была завершена. Пожалуйста, начните заново.")
                return ConversationHandler.END

            print(f"Получен телефон: {update.message.text}")  # Отладка

            registration.phone = update.message.text
            await sync_to_async(registration.save)()
            print(f"Телефон сохранен: {registration.phone}")  # Отладка

            await update.message.reply_text("Вы успешно зарегистрированы!")

            # Завершение процесса редактирования
            context.user_data.clear()
            print("Регистрация завершена.")  # Отладка
            return ConversationHandler.END

    except Exception as e:
        print(f"Error occurred: {e}")  # Логируем ошибку для отладки
        await update.message.reply_text("Что-то пошло не так. Попробуйте снова.")

    return ConversationHandler.END
