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


# кнопки для публичная оферта
public_offer_button = [[InlineKeyboardButton("Перейти к публичной оферте", url="https://goabay.com/ru/oferta/")]]
offerta_button = InlineKeyboardMarkup(public_offer_button)


# Создание списка кнопок и соответствующих callback_data
order_calculation_btn = [
    ("Стоимость товара", 'product_cost'),
    ("Доставка в РФ", 'delivery_rus'),
    ("Услуга GoaBay за 4кг", 'goabay_service'),
    ("Калькулятор", 'calculator')
]

# Создание кнопок
buttons = [InlineKeyboardButton(text=name, callback_data=data) for name, data in order_calculation_btn]
# Группировка кнопок в ряд (по 2 кнопки в строке)
order_calculation_btn = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
# Создание разметки клавиатуры
order_calculation_pay = InlineKeyboardMarkup(order_calculation_btn)

# Определяем инлайн-кнопки для исправления и подтверждения данных
back_cal_button = InlineKeyboardButton(text="Назад к расчету 🏧", callback_data='back_calculator')

# Создаем клавиатуру с этими кнопками
back_button_cal = InlineKeyboardMarkup([[back_cal_button]])


# Создание списка кнопок и соответствующих callback_data
qw_answ_btn_list = [
    ("Как оплатить заказ", 'answer_cost'),
    ("Что можно купить через нас", 'storage_india'),
    ("Тип платежа и скорость", 'order_speed'),
    ("Покупка и отправка", 'storage_service'),
    ("Обмен товара", 'calculator'),
    ("Возврат товара", 'calculator'),
]

# Создание кнопок
buttons = [InlineKeyboardButton(text=name, callback_data=data) for name, data in qw_answ_btn_list]
# Группировка кнопок в ряд (по 2 кнопки в строке)
qw_answ_btn = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
# Создание разметки клавиатуры
qw_answ_btn_main = InlineKeyboardMarkup(qw_answ_btn)

# Определяем инлайн-кнопки для исправления и подтверждения данных
back_qw_answ_button = InlineKeyboardButton(text="Назад к опрос-ответ 🏧", callback_data='back_qwe_answer')

# Создаем клавиатуру с этими кнопками
back_qw_answ_button_main = InlineKeyboardMarkup([[back_qw_answ_button]])
