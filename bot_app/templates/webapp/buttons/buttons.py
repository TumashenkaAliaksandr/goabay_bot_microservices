from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Определяем инлайн-кнопки для исправления и подтверждения данных
correct_button = InlineKeyboardButton(text="Исправить данные", callback_data='edit_data')
confirm_button = InlineKeyboardButton(text="Подтвердить", callback_data='confirm_data')

# Создаем клавиатуру с этими кнопками
confirmation_keyboard = InlineKeyboardMarkup([[correct_button, confirm_button]])


# Создание списка способов оплаты и соответствующих callback_data
payment_methods = [
    ("Qiwi", 'qiwi'),
    ("U-Money", 'u-money'),
    ("Bank Transfer", 'bank-transfer'),
    ("Paypal", 'paypal'),
    ("Western Union", 'western-union'),
    ("Ethereum", 'ethereum')
]

# Создание кнопок
buttons = [InlineKeyboardButton(text=name, callback_data=data) for name, data in payment_methods]

# Группировка кнопок в ряд (по 2 кнопки в строке)
keyboards = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

# Создание разметки клавиатуры
reply_markup_pay = InlineKeyboardMarkup(keyboards)

# Определяем инлайн-кнопки для исправления и подтверждения данных
back_pay_button = InlineKeyboardButton(text="Назад к Способам оплаты 🏧", callback_data='back_pay')

# Создаем клавиатуру с этими кнопками
back_button_go = InlineKeyboardMarkup([[back_pay_button]])
