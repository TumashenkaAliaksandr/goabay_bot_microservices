from telegram import Update
from telegram.ext import CallbackContext

from bot_app.ticket_store_button import main_markup


# Обработка команды /start
async def start(update: Update, context: CallbackContext) -> None:
    with open('templates/webapp/text_files_py_txt/welcome.txt', 'r', encoding='utf-8') as file:
        welcome_message = file.read()

    await update.message.reply_text(welcome_message, reply_markup=main_markup)


# Обработка команды /help
async def help(update: Update, context: CallbackContext) -> None:
    with open('templates/webapp/text_files_py_txt/welcome.txt', 'r', encoding='utf-8') as file:
        welcome_message = file.read()

    await update.message.reply_text(welcome_message, reply_markup=main_markup)
