import asyncio
import os
import re
import django
from asgiref.sync import sync_to_async
import logging
from telegram import Update
from telegram.ext import CallbackContext
from bot_app.send_rabbitmq import send_to_rabbitmq
from bot_app.templates.webapp.answers.info_back import messages_to_delete
from bot_app.templates.webapp.buttons.buttons_store import main_markup, change_profile_btn, profile_btn
from bot_app.templates.webapp.buttons.inline_category_store_btn import reg_reply_markup
from bot_app.templates.webapp.text_files_py_txt.reg_answer import reg_info
from bot_app.templates.webapp.text_files_py_txt.welcome_room import namaste

# Установка переменной окружения и инициализация Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goabay_bot.settings')
django.setup()

from bot_app.models import UserRegistration  # Import Django models here


def escape_markdown_v2(text: str) -> str:
    """Экранирует специальные символы для MarkdownV2."""
    # Список символов, которые нужно экранировать
    special_chars = r'._*[]()~`>#+\-|{}.!'
    # Используем регулярное выражение для замены символов на экранированные
    escaped_text = re.sub(f'([{re.escape(special_chars)}])', r'\\\1', text)
    return escaped_text


async def show_user_info(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    # Получаем данные пользователя
    registration = await sync_to_async(UserRegistration.objects.get)(user_id=user_id)

    # Формируем сообщение с данными пользователя
    user_info = (f"📌\n\n🧩👳‍♂️Ваши данные:\n\n"
                 f"────⋆⋅☆⋅⋆──\n\n"
                 f"👥 Имя: {registration.name}\n"
                 f"〰️〰️〰️\n"
                 f"📬 Email: {registration.email}\n"
                 f"〰️〰️〰️\n"
                 f"☎️ Телефон: {registration.phone}\n"
                 f"\n────⋆⋅☆⋅⋆──\n")

    # Экранируем сообщение перед отправкой
    escaped_user_info = escape_markdown_v2(user_info)
    # Удаляем все сообщения из списка, если они были отправлены ранее
    for msg in messages_to_delete:
        try:
            await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

        except Exception as e:

            logging.error(f"Ошибка при удалении сообщения: {e}")

    # Очищаем список после удаления

    messages_to_delete.clear()

    # Отправляем сообщение с данными пользователя и меню
    info_profile_message = await update.message.reply_text(escaped_user_info, parse_mode='MarkdownV2')
    messages_to_delete.append(info_profile_message)  # Добавляем в список для удаления

    # Отправляем только клавиатуру с минимальным текстом
    get_back_profile_info = await update.message.reply_text(
        '🙌 Выберите что вас интересует:',
        reply_markup=change_profile_btn
    )
    messages_to_delete.append(get_back_profile_info)


# Обработчик для кнопки "👳‍♂️ Мои данные"
async def profile_button_handler(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    message = update.message.text
    send_to_rabbitmq(message)
    # Удаление старого сообщения пользователя через 0.1 секунды
    await asyncio.sleep(0.1)
    try:
        await update.message.delete()  # Удаляем исходное сообщение пользователя
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения: {e}")

    # Если сообщение пришло от кнопки "Личный кабинет 👤"
    if message == "Личный кабинет 👤":
        # Проверяем, зарегистрирован ли пользователь
        registration = await sync_to_async(UserRegistration.objects.filter(user_id=user_id).first)()

        if registration and registration.is_registered:
            # Экранируем сообщение перед отправкой
            # escaped_user_info = escape_markdown_v2(namaste)
            # Если пользователь зарегистрирован, показываем кнопку "Мои данные 👳‍♂️"
            profile_message = await update.message.reply_text(namaste, parse_mode='MarkdownV2', reply_markup=profile_btn)
            messages_to_delete.append(profile_message)  # Добавляем в список для удаления

            # Отправляем только клавиатуру с минимальным текстом
            get_back_profile = await update.message.reply_text(
                '🙌 Выберите что вас интересует:',
                reply_markup=profile_btn
            )
            messages_to_delete.append(get_back_profile)
        else:
            await update.message.reply_text(
                reg_info, parse_mode='MarkdownV2',
                reply_markup=reg_reply_markup,
            )

    # Если сообщение пришло от кнопки "Мои данные 👳‍♂️"
    elif message == "👳‍♂️ Мои данные":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        # Отображаем данные пользователя
        show_profile_message = await show_user_info(update, context)
        messages_to_delete.append(show_profile_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        # get_back_show_profile = await update.message.reply_text(
        #     '🙌 Выберите что вас интересует:',
        #     reply_markup=change_profile_btn
        # )
        # messages_to_delete.append(get_back_show_profile)

    else:
        # Если нажата неизвестная кнопка
        await update.message.reply_text('🙌 Выберите что вас интересует:', reply_markup=main_markup)
