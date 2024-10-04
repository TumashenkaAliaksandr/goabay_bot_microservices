from telegram import ReplyKeyboardMarkup, KeyboardButton


# кнопки для "Как мы работаем"
goa_pay_btn = ReplyKeyboardMarkup([
    [KeyboardButton("Способы оплаты 💵"), KeyboardButton("Как мы работаем ⌛️️"), KeyboardButton("Расчет заказа 💰")],
    [KeyboardButton("⬅️ Назад к информации")]
], resize_keyboard=True)