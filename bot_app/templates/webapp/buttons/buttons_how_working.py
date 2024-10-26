from telegram import ReplyKeyboardMarkup, KeyboardButton


# кнопки для "Как мы работаем"
goa_pay_btn = ReplyKeyboardMarkup([
    [KeyboardButton("Способы оплаты 🏧"), KeyboardButton("Расчет заказа 💰")],
    [KeyboardButton("⬅️ Назад к информации")]
], resize_keyboard=True)


# кнопки для "Доставка"
delivery_btn = ReplyKeyboardMarkup([
    [KeyboardButton("📝 Информация о Доставке"), ("📑 Способы Доставки"), KeyboardButton("👀 Отследить заказ")],
    [KeyboardButton("⬅️ Назад к информации")]
], resize_keyboard=True)


# кнопки для "склад в Индии"
warehouse_btn = ReplyKeyboardMarkup([
    [KeyboardButton("🏗 Как работает Склад"), KeyboardButton("🛍 Товары на складе")],
    [KeyboardButton("⬅️ Товары из Индии")]
], resize_keyboard=True)
