from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from bot_app.models import UserRegistration
from bot_app.templates.webapp.buttons.buttons_store import profile_btn
from asgiref.sync import sync_to_async


async def store_registration_handler(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    message_text = update.message.text

    # Асинхронное получение или создание записи пользователя
    registration, created = await sync_to_async(UserRegistration.objects.get_or_create)(user_id=user_id)

    # Отладочные сообщения
    print(f"Received message: {message_text}")
    print(f"Current registration step: {registration.step}")

    # Обработка нажатия кнопки "Личный кабинет"
    if message_text == "👤 Личный кабинет":
        if registration.is_registered:
            # Если пользователь зарегистрирован, просто уведомляем о входе в кабинет
            await update.message.reply_text(
                "👳‍♀️ Вы успешно вошли в личный кабинет.",
                reply_markup=profile_btn  # Предполагается, что profile_btn определён где-то в вашем коде
            )
            return ConversationHandler.END  # Завершаем разговор

        else:
            # Если пользователь не зарегистрирован, предлагаем пройти регистрацию
            await update.message.reply_text(
                "***Вы еще не зарегистрированы!***\n"
                "***Пожалуйста, пройдите регистрацию.***\n\n"
                "_Пожалуйста, ✍️ введите ваше имя:_",
                parse_mode='MarkdownV2'
            )

            # Устанавливаем шаг на имя и сохраняем состояние
            registration.step = 'name'
            await sync_to_async(registration.save)()  # Сохраняем изменения в базе данных

            return 1  # Переход к шагу ввода имени

    if message_text == "✏️ Редактировать данные":
        registration.step = None  # Сброс шага
        registration.is_registered = False  # Установка флага на не зарегистрированного
        await sync_to_async(registration.save)()

        # Начинаем процесс регистрации заново
        await update.message.reply_text(
            "***Для того чтобы делать покупки в магазине 🏪 GoaBay***\n"
            "***Нужно пройти 📜 РЕГИСТРАЦИЮ***\n\n"
            "_Пожалуйста, ✍️ введите ваше имя:_",
            parse_mode='MarkdownV2'
        )
        registration.step = 'name'  # Устанавливаем шаг на имя
        await sync_to_async(registration.save)()
        return 1  # Переход к шагу ввода имени

    if registration.is_registered and registration.step is None:
        await update.message.reply_text('Вы вошли в профиль.', reply_markup=profile_btn)
        return ConversationHandler.END

    if registration.step == 'name':
        # Сохраняем имя пользователя и просим ввести email
        registration.name = message_text
        registration.step = 'email'
        await sync_to_async(registration.save)()
        await update.message.reply_text(
            "*Отлично 👍*\n\n"
            "_Теперь введите 📧 ваш email:_",
            parse_mode='MarkdownV2'
        )
        return 2  # Переход к шагу ввода email

    elif registration.step == 'email':
        # Сохраняем email и просим ввести телефон
        registration.email = message_text
        registration.step = 'phone'
        await sync_to_async(registration.save)()
        await update.message.reply_text(
            "*Отлично 👍*\n\n"
            "_Теперь введите ☎️ ваш телефонный номер:_",
            parse_mode='MarkdownV2'
        )
        return 3  # Переход к шагу ввода телефона

    elif registration.step == 'phone':
        # Сохраняем телефон и завершаем регистрацию
        registration.phone = message_text
        registration.is_registered = True
        await sync_to_async(registration.save)()

        user_info = (f"Ваши данные:\n"
                     f"Имя: {registration.name}\n"
                     f"📧 Email: {registration.email}\n"
                     f"☎️Телефон: {registration.phone}\n\n"
                     "☑️ Регистрация завершена успешно\! Спасибо\!")

        await update.message.reply_text('👳‍♀️ Ваш Профиль:', reply_markup=profile_btn)

        return ConversationHandler.END

    else:
        print(f"Unknown step or command: {registration.step}, message: {message_text}")

        await update.message.reply_text("Что-то пошло не так. Попробуйте снова.")

        return ConversationHandler.END
