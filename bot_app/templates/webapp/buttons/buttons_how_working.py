from telegram import ReplyKeyboardMarkup, KeyboardButton


# кнопки для "Как мы работаем"
goa_pay_btn = ReplyKeyboardMarkup([
    [KeyboardButton("Способы оплаты 🏧"), KeyboardButton("Расчет заказа 💰")],
    [KeyboardButton("⬅️ Назад к информации")]
], resize_keyboard=True)


# кнопки для "Доставка"
delivery_btn = ReplyKeyboardMarkup([
    [KeyboardButton("📝 Информация о Доставке"), ("📑 Способы Доставки"), KeyboardButton("👀 Отследить заказ")],
    [KeyboardButton("⬅️ Как мы работаем 🛠")]
], resize_keyboard=True)


# кнопки для "склад в Индии"
warehouse_btn = ReplyKeyboardMarkup([
    [KeyboardButton("🛍 Товары на складе"), ("🏗 Как работает Склад")],
    [KeyboardButton("⬅️ Товары из Индии"), KeyboardButton("🔗 Ввести ссылку Goabay")]
], resize_keyboard=True)


# кнопки для "🛒 Мои Покупки"
pays_btn = ReplyKeyboardMarkup([
    [KeyboardButton("📜 История"), ("🛒")],
    [KeyboardButton("🔙 Назад в кабинет")]
], resize_keyboard=True)
