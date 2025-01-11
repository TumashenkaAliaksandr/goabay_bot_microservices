from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from bot_app.models import UserRegistration  # Импортируем модель UserRegistration
from asgiref.sync import sync_to_async
from bot_app.templates.webapp.profile.profile_date import show_user_info, profile_button_handler
from bot_app.templates.webapp.text_files_py_txt.reg_answer import reg_info

# Константы для состояний ConversationHandler
STEP_EDIT_NAME = 1
STEP_EDIT_EMAIL = 2
STEP_EDIT_PHONE = 3


# async def registration_handler(update: Update, context: CallbackContext) -> int:
#     if update.callback_query:
#         query = update.callback_query
#         await query.answer()
#         user_id = query.from_user.id
#         message_text = query.data
#     else:
#         user_id = update.message.from_user.id
#         message_text = update.message.text
#
#     print(f"Обработка сообщения '{message_text}' от пользователя {user_id}.")
#
#     # Получаем регистрацию пользователя асинхронно
#     registrations = await sync_to_async(list)(UserRegistration.objects.filter(user_id=user_id))
#
#     try:
#         # Обработка запроса личного кабинета
#         if message_text == "Личный кабинет 👤":
#             if registrations:
#                 registration = registrations[0]
#                 if registration.is_registered:
#                     await show_user_info(update, context)
#                     return ConversationHandler.END
#
#             # Отображение кнопок для начала регистрации
#             keyboard = [
#                 [InlineKeyboardButton("Начать регистрацию", callback_data="start_registration")],
#                 [InlineKeyboardButton("Отменить регистрацию", callback_data="end_registration")],
#             ]
#             reply_markup = InlineKeyboardMarkup(keyboard)
#
#             await update.message.reply_text(
#                 reg_info, parse_mode='MarkdownV2',
#                 reply_markup=reply_markup,
#             )
#             return ConversationHandler.END
#
#         # Шаг регистрации
#         step = context.user_data.get('step', STEP_EDIT_NAME)
#
#         # Логирование текущего шага
#         print(f"Текущий шаг: {step}")
#
#         # Если шаг не установлен, запрашиваем имя пользователя
#         if step == STEP_EDIT_NAME:
#             print("Шаг не установлен. Запрашиваем имя пользователя.")
#             await context.bot.send_message(chat_id=update.effective_user.id, text="Пожалуйста, введите ваше имя:")
#             context.user_data['step'] = STEP_EDIT_NAME  # Устанавливаем шаг
#             return STEP_EDIT_NAME
#
#         # Шаг редактирования имени
#         elif step == STEP_EDIT_NAME:
#             print(f"[DEBUG] Получено имя: {message_text}")  # Лог
#             if not message_text.strip():  # Проверка на пустое имя
#                 await context.bot.send_message(chat_id=user_id, text="Имя не может быть пустым. Попробуйте снова:")
#                 return STEP_EDIT_NAME
#
#             # Сохраняем имя пользователя
#             registration, created = await sync_to_async(UserRegistration.objects.get_or_create)(user_id=user_id)
#             registration.name = message_text.strip()
#             await sync_to_async(registration.save)()
#
#             print(f"[DEBUG] Имя сохранено: {registration.name}")  # Лог сохраненного имени
#             await context.bot.send_message(chat_id=user_id, text="Спасибо! Теперь введите ваш email:")
#
#             # Обновляем шаг для перехода к email
#             context.user_data['step'] = STEP_EDIT_EMAIL
#             print(f"[DEBUG] Переход на шаг: {STEP_EDIT_EMAIL}")
#             return STEP_EDIT_EMAIL
#
#         # Шаг редактирования email
#         elif step == STEP_EDIT_EMAIL:
#             print(f"[DEBUG] Получен email: {message_text}")  # Лог
#             if '@' not in message_text or '.' not in message_text:  # Проверка email
#                 await context.bot.send_message(chat_id=user_id, text="Неверный формат email. Попробуйте снова:")
#                 return STEP_EDIT_EMAIL
#
#             registration = await sync_to_async(UserRegistration.objects.filter(user_id=user_id).first)()
#             registration.email = message_text.strip()
#             await sync_to_async(registration.save)()
#             await context.bot.send_message(chat_id=user_id, text="Отлично! Теперь введите ваш телефонный номер:")
#
#             # Обновляем шаг для перехода к телефону
#             context.user_data['step'] = STEP_EDIT_PHONE
#             print(f"[DEBUG] Переход на шаг: {STEP_EDIT_PHONE}")
#             return STEP_EDIT_PHONE
#
#         # Шаг редактирования телефона
#         elif step == STEP_EDIT_PHONE:
#             print(f"[DEBUG] Получен телефон: {message_text}")  # Лог
#             if not message_text.isdigit():  # Проверка на цифры
#                 await context.bot.send_message(chat_id=user_id,
#                                                text="Телефон должен содержать только цифры. Попробуйте снова:")
#                 return STEP_EDIT_PHONE
#
#             registration = await sync_to_async(UserRegistration.objects.filter(user_id=user_id).first)()
#             registration.phone = message_text.strip()
#             registration.is_registered = True  # Устанавливаем флаг завершенной регистрации
#             await sync_to_async(registration.save)()
#             await context.bot.send_message(chat_id=user_id, text="Вы успешно зарегистрированы!")
#
#             # Завершаем регистрацию
#             context.user_data.clear()  # Очищаем данные пользователя
#             print("[DEBUG] Регистрация завершена.")  # Лог
#             return ConversationHandler.END
#
#     except Exception as e:
#         print(f"Ошибка: {e}")
#         await update.message.reply_text("Что-то пошло не так. Попробуйте снова.")
#
#     return ConversationHandler.END


async def registration_handler(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    message_text = update.message.text  # Получаем текст сообщения от пользователя

    # Проверка, если сообщение пришло от кнопки
    if message_text == 'Личный кабинет 👤':
        # Проверяем, зарегистрирован ли пользователь
        registration = await sync_to_async(UserRegistration.objects.filter(user_id=user_id).first)()
        if registration and registration.is_registered:
            # Если пользователь зарегистрирован, переходим в личный кабинет
            await profile_button_handler(update, context)  # Вызов обработчика профиля
            return ConversationHandler.END  # Завершаем регистрацию и переходим в личный кабинет

        # Если пользователь не зарегистрирован, начинаем регистрацию
        await context.bot.send_message(chat_id=user_id, text=reg_info, parse_mode='MarkdownV2')
        context.user_data['step'] = STEP_EDIT_NAME  # Устанавливаем шаг на ввод имени
        await context.bot.send_message(chat_id=user_id, text="Пожалуйста, введите ваше имя:")
        return STEP_EDIT_NAME  # Переход к следующему шагу

    # Получаем текущий шаг
    step = context.user_data.get('step', STEP_EDIT_NAME)

    print(f"Текущий шаг: {step}")

    # Шаг редактирования имени
    if step == STEP_EDIT_NAME:
        print(f"[DEBUG] Получено имя: {message_text}")
        if not message_text.strip():  # Если имя пустое
            await context.bot.send_message(chat_id=user_id, text="Имя не может быть пустым. Попробуйте снова:")
            return STEP_EDIT_NAME

        # Сохраняем имя пользователя
        registration, created = await sync_to_async(UserRegistration.objects.get_or_create)(user_id=user_id)
        registration.name = message_text.strip()
        await sync_to_async(registration.save)()

        print(f"[DEBUG] Имя сохранено: {registration.name}")  # Лог сохраненного имени
        await context.bot.send_message(chat_id=user_id, text="Спасибо! Теперь введите ваш email:")

        # Обновляем шаг для перехода к email
        context.user_data['step'] = STEP_EDIT_EMAIL  # Переход на следующий шаг
        print(f"[DEBUG] Переход на шаг: {STEP_EDIT_EMAIL}")
        return STEP_EDIT_EMAIL

    # Шаг редактирования email
    elif step == STEP_EDIT_EMAIL:
        print(f"[DEBUG] Получен email: {message_text}")  # Лог
        if '@' not in message_text or '.' not in message_text:  # Проверка email
            await context.bot.send_message(chat_id=user_id, text="Неверный формат email. Попробуйте снова:")
            return STEP_EDIT_EMAIL

        registration = await sync_to_async(UserRegistration.objects.filter(user_id=user_id).first)()
        registration.email = message_text.strip()
        await sync_to_async(registration.save)()
        await context.bot.send_message(chat_id=user_id, text="Отлично! Теперь введите ваш телефонный номер:")

        # Обновляем шаг для перехода к телефону
        context.user_data['step'] = STEP_EDIT_PHONE
        print(f"[DEBUG] Переход на шаг: {STEP_EDIT_PHONE}")
        return STEP_EDIT_PHONE

    # Шаг редактирования телефона
    elif step == STEP_EDIT_PHONE:
        print(f"[DEBUG] Получен телефон: {message_text}")  # Лог
        if not message_text.isdigit():  # Проверка на цифры
            await context.bot.send_message(chat_id=user_id,
                                           text="Телефон должен содержать только цифры. Попробуйте снова:")
            return STEP_EDIT_PHONE

        registration = await sync_to_async(UserRegistration.objects.filter(user_id=user_id).first)()
        registration.phone = message_text.strip()
        registration.is_registered = True  # Устанавливаем флаг завершенной регистрации
        await sync_to_async(registration.save)()
        await context.bot.send_message(chat_id=user_id, text="Вы успешно зарегистрированы!")

        # Завершаем регистрацию
        context.user_data.clear()  # Очищаем данные пользователя
        print("[DEBUG] Регистрация завершена.")  # Лог
        # Переходим в личный кабинет после завершения регистрации
        await profile_button_handler(update, context)  # Вызов обработчика профиля
        return ConversationHandler.END

    return ConversationHandler.END



# async def registration_handler(update: Update, context: CallbackContext) -> int:
#     user_id = update.message.from_user.id
#     message_text = update.message.text  # Получаем текст сообщения от пользователя
#
#     # Проверка, если сообщение пришло от кнопки
#     if message_text == 'Личный кабинет 👤':
#         await context.bot.send_message(chat_id=user_id, text=reg_info, parse_mode='MarkdownV2')
#         context.user_data['step'] = STEP_EDIT_NAME  # Устанавливаем шаг на ввод имени
#         await context.bot.send_message(chat_id=user_id, text="Пожалуйста, введите ваше имя:")
#         return STEP_EDIT_NAME  # Переход к следующему шагу
#
#     # Получаем текущий шаг
#     step = context.user_data.get('step', STEP_EDIT_NAME)
#
#     print(f"Текущий шаг: {step}")
#
#     # Шаг редактирования имени
#     if step == STEP_EDIT_NAME:
#         print(f"[DEBUG] Получено имя: {message_text}")
#         if not message_text.strip():  # Если имя пустое
#             await context.bot.send_message(chat_id=user_id, text="Имя не может быть пустым. Попробуйте снова:")
#             return STEP_EDIT_NAME
#
#         # Сохраняем имя пользователя
#         registration, created = await sync_to_async(UserRegistration.objects.get_or_create)(user_id=user_id)
#         registration.name = message_text.strip()
#         await sync_to_async(registration.save)()
#
#         print(f"[DEBUG] Имя сохранено: {registration.name}")  # Лог сохраненного имени
#         await context.bot.send_message(chat_id=user_id, text="Спасибо! Теперь введите ваш email:")
#
#         # Обновляем шаг для перехода к email
#         context.user_data['step'] = STEP_EDIT_EMAIL  # Переход на следующий шаг
#         print(f"[DEBUG] Переход на шаг: {STEP_EDIT_EMAIL}")
#         return STEP_EDIT_EMAIL
#
#     # Шаг редактирования email
#     elif step == STEP_EDIT_EMAIL:
#         print(f"[DEBUG] Получен email: {message_text}")  # Лог
#         if '@' not in message_text or '.' not in message_text:  # Проверка email
#             await context.bot.send_message(chat_id=user_id, text="Неверный формат email. Попробуйте снова:")
#             return STEP_EDIT_EMAIL
#
#         registration = await sync_to_async(UserRegistration.objects.filter(user_id=user_id).first)()
#         registration.email = message_text.strip()
#         await sync_to_async(registration.save)()
#         await context.bot.send_message(chat_id=user_id, text="Отлично! Теперь введите ваш телефонный номер:")
#
#         # Обновляем шаг для перехода к телефону
#         context.user_data['step'] = STEP_EDIT_PHONE
#         print(f"[DEBUG] Переход на шаг: {STEP_EDIT_PHONE}")
#         return STEP_EDIT_PHONE
#
#     # Шаг редактирования телефона
#     elif step == STEP_EDIT_PHONE:
#         print(f"[DEBUG] Получен телефон: {message_text}")  # Лог
#         if not message_text.isdigit():  # Проверка на цифры
#             await context.bot.send_message(chat_id=user_id,
#                                            text="Телефон должен содержать только цифры. Попробуйте снова:")
#             return STEP_EDIT_PHONE
#
#         registration = await sync_to_async(UserRegistration.objects.filter(user_id=user_id).first)()
#         registration.phone = message_text.strip()
#         registration.is_registered = True  # Устанавливаем флаг завершенной регистрации
#         await sync_to_async(registration.save)()
#         await context.bot.send_message(chat_id=user_id, text="Вы успешно зарегистрированы!")
#
#         # Завершаем регистрацию
#         context.user_data.clear()  # Очищаем данные пользователя
#         print("[DEBUG] Регистрация завершена.")  # Лог
#         return ConversationHandler.END
#
#     return ConversationHandler.END
