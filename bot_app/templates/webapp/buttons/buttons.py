from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Определяем инлайн-кнопки для исправления и подтверждения данных
correct_button = InlineKeyboardButton(text="Исправить данные", callback_data='edit_data')
confirm_button = InlineKeyboardButton(text="Подтвердить", callback_data='confirm_data')

# Создаем клавиатуру с этими кнопками
confirmation_keyboard = InlineKeyboardMarkup([[correct_button, confirm_button]])
