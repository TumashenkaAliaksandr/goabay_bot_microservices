# buttons_store.py
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


# Маркап
main_markup = ReplyKeyboardMarkup([
    [KeyboardButton("Товары из Индии 👳‍♀️"), KeyboardButton("Как мы работаем ⌚️")],
    [KeyboardButton("Сервис 🔧"), KeyboardButton("О компании 🏢")],
    [KeyboardButton("Наш Блог 📚"), KeyboardButton("Личный кабинет 👤")]
], resize_keyboard=True)

# кнопки для "Товары из Индии"
products_btn_india = ReplyKeyboardMarkup([
    [KeyboardButton("📁 Каталог"), KeyboardButton("🏪 Склад В Индии"), KeyboardButton("📈 Лидеры продаж")],
    [KeyboardButton("⭐️ Рекомендуем"), KeyboardButton("🎁 Подарки"), KeyboardButton("🎉 Акции")],
    [KeyboardButton("⬅️ Назад")]
], resize_keyboard=True)



# кнопки для "Как мы работаем"
how_we_work_btn = ReplyKeyboardMarkup([
    [KeyboardButton("🚚 Доставка"), KeyboardButton("💳 Оплата"), KeyboardButton("🗣 ЧаВо")],
    [KeyboardButton("🚨 Помощь"), KeyboardButton("💸 Курс валют"), KeyboardButton("🤝 Наши партнёры")],
    [KeyboardButton("⬅️ Назад")]
], resize_keyboard=True)


# кнопки для "Сервис"
service_btn = ReplyKeyboardMarkup([
    [KeyboardButton("✈️ Авиабилеты"), KeyboardButton("🏘 Гоа Аренда"), KeyboardButton("🏞 Экскурсии по Гоа")],
    [KeyboardButton("🎬 Реклама на сайте"), KeyboardButton("🎉 Акции"), KeyboardButton("📰 Новости компании")],
    [KeyboardButton("⬅️ Назад")]
], resize_keyboard=True)


# Инлайн кнопки для "О компании"
about_btn = ReplyKeyboardMarkup([
    [KeyboardButton("Как мы работаем ⌚️"), KeyboardButton("Отзывы 💬"), KeyboardButton("Публичная оферта 📜")],
    [KeyboardButton("Партнерская програма 👥"), KeyboardButton("Свяаться с нами 📲"), KeyboardButton("Обсуждения 📢")],
    [KeyboardButton("⬅️ Назад")]
], resize_keyboard=True)


# кнопки для "Наш Блог"
blog_btn = ReplyKeyboardMarkup([
    [KeyboardButton("🏋️‍♂️️ Красота и здоровье"), KeyboardButton("🥗 Кулинария"), KeyboardButton("👳‍♂️ Культура")],
    [KeyboardButton("💅 Мода"), KeyboardButton("📰 Новости"), KeyboardButton("📺 Политика")],
    [KeyboardButton("🧗‍♀️ Туризм"), KeyboardButton("🧗‍♀️ Фэншуй"), KeyboardButton("📊 Экономика")],
    [KeyboardButton("⬅️ Назад")]
], resize_keyboard=True)


# кнопки для "Личный Кабинет"
profile_btn = ReplyKeyboardMarkup([
    [KeyboardButton("👳‍♂️ Мои данные"), KeyboardButton("🛒 Мои Покупки"), KeyboardButton("🗂 Мои Документы")],
    # [KeyboardButton("📈 Лидеры продаж"), KeyboardButton("⭐️ Рекомендуем"), KeyboardButton("🎉 Акции")],
    # [KeyboardButton("✍️ Регистрация на рейс"), KeyboardButton("🎁 Подарки")],
    [KeyboardButton("⬅️ Назад")]
], resize_keyboard=True)


change_profile_btn = ReplyKeyboardMarkup([
    ["✏️ Редактировать данные", "🔙 Назад в кабинет"]
], resize_keyboard=True)
