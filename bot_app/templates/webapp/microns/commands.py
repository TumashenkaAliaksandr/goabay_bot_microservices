from telegram import Update
from telegram.ext import CallbackContext
import os

from bot_app.templates.webapp.buttons.ticket_store_button import main_markup


# Получение пути к файлу welcome.txt
def get_welcome_message_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Путь к текущему файлу
    return os.path.join(base_dir, '../../webapp/text_files_py_txt/welcome.txt')  # Путь к welcome.txt


# Обработка команды /start
async def start(update: Update, context: CallbackContext) -> None:
    welcome_message_path = get_welcome_message_path()

    try:
        with open(welcome_message_path, 'r', encoding='utf-8') as file:
            welcome_message = file.read()
        await update.message.reply_text(welcome_message, reply_markup=main_markup)
    except FileNotFoundError:
        await update.message.reply_text("Файл приветственного сообщения не найден.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при чтении файла: {e}")


# Обработка команды /help
async def help(update: Update, context: CallbackContext) -> None:
    welcome_message_path = get_welcome_message_path()

    try:
        with open(welcome_message_path, 'r', encoding='utf-8') as file:
            welcome_message = file.read()
        await update.message.reply_text(welcome_message, reply_markup=main_markup)
    except FileNotFoundError:
        await update.message.reply_text("Файл Help сообщения не найден.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при чтении файла: {e}")
