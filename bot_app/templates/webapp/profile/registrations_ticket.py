from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from bot_app.models import UserRegistration  # Импортируем модель UserRegistration
from asgiref.sync import sync_to_async
from bot_app.templates.webapp.profile.profile_date import show_user_info
from bot_app.templates.webapp.profile.registrations_store import STEP_EDIT_EMAIL, STEP_EDIT_PHONE, STEP_EDIT_NAME


async def ticket_registration_handler(update: Update, context: CallbackContext) -> int:
    try:
        # Определяем источник сообщения (callback или текст)
        if update.callback_query:
            query = update.callback_query
            await query.answer()  # Обязательно отвечаем на callback
            user_id = query.from_user.id  # ID пользователя из callback
            message_text = query.data  # Используем данные кнопки как текст
        else:
            if not update.message:
                print("[DEBUG] Сообщение пользователя отсутствует.")
                await context.bot.send_message(chat_id=update.effective_user.id, text="Пожалуйста, введите ваше имя:")
                return STEP_EDIT_NAME

            user_id = update.message.from_user.id  # ID пользователя из текстового сообщения
            message_text = update.message.text  # Текст сообщения

        print(f"[DEBUG] Обработка сообщения '{message_text}' от пользователя {user_id}.")  # Логируем запрос

        # Получаем регистрацию пользователя
        registrations = await sync_to_async(list)(UserRegistration.objects.filter(user_id=user_id))

        # Если пользователь не зарегистрирован, запрашиваем имя
        if not registrations:
            print("[DEBUG] Пользователь не зарегистрирован. Запрашиваем имя.")  # Лог
            await context.bot.send_message(chat_id=user_id, text="Пожалуйста, введите ваше имя:")
            context.user_data['step'] = 'edit_name'
            return STEP_EDIT_NAME

        registration = registrations[0]  # Предполагаем, что пользователь только один
        if registration.is_registered:
            await show_user_info(update, context)  # Отображаем данные пользователя
            return ConversationHandler.END

        # Обработка текущего шага
        step = context.user_data.get('step', 'edit_name')  # Если шаг отсутствует, начинаем с имени

        if step == 'edit_name':
            print(f"[DEBUG] Получено имя: {message_text}")  # Лог
            if not message_text.strip():  # Проверяем пустой ввод
                await context.bot.send_message(chat_id=user_id, text="Имя не может быть пустым. Попробуйте снова:")
                return STEP_EDIT_NAME

            registration.name = message_text.strip()
            await sync_to_async(registration.save)()
            await context.bot.send_message(chat_id=user_id, text="Спасибо! Теперь введите ваш email:")
            context.user_data['step'] = 'edit_email'
            return STEP_EDIT_EMAIL

        elif step == 'edit_email':
            print(f"[DEBUG] Получен email: {message_text}")  # Лог
            if '@' not in message_text or '.' not in message_text:  # Простейшая проверка email
                await context.bot.send_message(chat_id=user_id, text="Неверный формат email. Попробуйте снова:")
                return STEP_EDIT_EMAIL

            registration.email = message_text.strip()
            await sync_to_async(registration.save)()
            await context.bot.send_message(chat_id=user_id, text="Отлично! Теперь введите ваш телефонный номер:")
            context.user_data['step'] = 'edit_phone'
            return STEP_EDIT_PHONE

        elif step == 'edit_phone':
            print(f"[DEBUG] Получен телефон: {message_text}")  # Лог
            if not message_text.isdigit():  # Проверка, что телефон состоит из цифр
                await context.bot.send_message(chat_id=user_id, text="Телефон должен содержать только цифры. Попробуйте снова:")
                return STEP_EDIT_PHONE

            registration.phone = message_text.strip()
            registration.is_registered = True  # Устанавливаем флаг завершенной регистрации
            await sync_to_async(registration.save)()
            await context.bot.send_message(chat_id=user_id, text="Вы успешно зарегистрированы!")

            # Завершение процесса регистрации
            context.user_data.clear()  # Очищаем данные пользователя
            print("[DEBUG] Регистрация завершена.")  # Лог
            return ConversationHandler.END

    except Exception as e:
        print(f"[ERROR] Произошла ошибка: {e}")  # Логируем ошибку
        await context.bot.send_message(chat_id=update.effective_user.id, text="Произошла ошибка. Попробуйте снова.")
        return ConversationHandler.END
