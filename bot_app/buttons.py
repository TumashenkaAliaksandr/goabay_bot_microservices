# buttons.py
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Маркап
markup = ReplyKeyboardMarkup([
    [KeyboardButton("Товары из Индии 👳‍♀️"), KeyboardButton("Как мы работаем ⌚️")],
    [KeyboardButton("Сервис 🔧"), KeyboardButton("О компании 🏢")],
    [KeyboardButton("Наш Блог 📚")]
], resize_keyboard=True)

# Инлайн кнопки для "Товары из Индии"
inline_buttons_india = [
    [
        InlineKeyboardButton("Каталог", callback_data="catalog"),
        InlineKeyboardButton("Склад В Индии", callback_data="warehouse"),
        InlineKeyboardButton("Лидеры продаж", callback_data="best_sellers")
    ],
    [
        InlineKeyboardButton("Рекомендуем", callback_data="recommended"),
        InlineKeyboardButton("Подарки", callback_data="gifts"),
        InlineKeyboardButton("Акции", callback_data="sales")
    ]
]

inline_markup_india = InlineKeyboardMarkup(inline_buttons_india)

# Инлайн кнопки для "Как мы работаем"
inline_buttons_how_we_work = [
    [
        InlineKeyboardButton("Доставка", callback_data="delivery"),
        InlineKeyboardButton("Оплата", callback_data="payment"),
        InlineKeyboardButton("ЧаВо", callback_data="faq")
    ],
    [
        InlineKeyboardButton("Помощь", callback_data="help"),
        InlineKeyboardButton("Курс валют", callback_data="currency"),
        InlineKeyboardButton("Наши партнёры", callback_data="partners")
    ]
]

inline_markup_how_we_work = InlineKeyboardMarkup(inline_buttons_how_we_work)

# Инлайн кнопки для "Сервис"
inline_buttons_service = [
    [
        InlineKeyboardButton("Авиабилеты", callback_data="flights"),
        InlineKeyboardButton("Гоа Аренда", callback_data="goa_rental"),
        InlineKeyboardButton("Экскурсии по Гоа", callback_data="goa_tours")
    ],
    [
        InlineKeyboardButton("Реклама на сайте", callback_data="advertising"),
        InlineKeyboardButton("Акции", callback_data="about_sales"),
        InlineKeyboardButton("Новости компании", callback_data="news")
    ]
]

inline_markup_service = InlineKeyboardMarkup(inline_buttons_service)

# Инлайн кнопки для "О компании"
inline_buttons_about = [
    [
        InlineKeyboardButton("Как мы работаем", callback_data="about_how_we_work"),
        InlineKeyboardButton("Отзывы", callback_data="reviews"),
        InlineKeyboardButton("Публичная оферта", callback_data="public_offer")
    ],
    [
        InlineKeyboardButton("Партнерская програма", callback_data="partnership_program"),
        InlineKeyboardButton("Свяаться с нами", callback_data="contact_us"),
        InlineKeyboardButton("Обсуждения", callback_data="discussions")
    ]
]

inline_markup_about = InlineKeyboardMarkup(inline_buttons_about)

# Инлайн кнопки для "Наш Блог"
inline_buttons_blog = [
    [
        InlineKeyboardButton("Красота и здоровье", callback_data="beauty_health"),
        InlineKeyboardButton("Кулинария", callback_data="cooking"),
        InlineKeyboardButton("Культура", callback_data="culture")
    ],
    [
        InlineKeyboardButton("Мода", callback_data="fashion"),
        InlineKeyboardButton("Новости", callback_data="news"),
        InlineKeyboardButton("Политика", callback_data="politics")
    ],
    [
        InlineKeyboardButton("Туризм", callback_data="tourism"),
        InlineKeyboardButton("Фэншуй", callback_data="feng_shui"),
        InlineKeyboardButton("Экономика", callback_data="economy")
    ]
]

inline_markup_blog = InlineKeyboardMarkup(inline_buttons_blog)
