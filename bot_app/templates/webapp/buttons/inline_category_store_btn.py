from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot_app.models import Product


# Функция для создания клавиатуры категорий
def create_category_keyboard():
    keyboard = [
        [InlineKeyboardButton("🌴 Товары из Индии 👳‍♂️", callback_data="category_indian_goods")],
        [InlineKeyboardButton("🏁 Мотоциклы 🏍", callback_data="category_motorcycles")],
        [InlineKeyboardButton("🇮🇳 Индийские бренды 👔️", callback_data="category_indian_brands")],
        [InlineKeyboardButton("💍 Сувениры и подарки 🎁", callback_data="category_souvenirs")],
        [InlineKeyboardButton("🍵 Индийский чай 🌿", callback_data="category_indian_tea")],
        [InlineKeyboardButton("🥫 Индийские специи 🌶", callback_data="category_indian_spices")],
        [InlineKeyboardButton("🥢 Благовония 🪔", callback_data="category_incense")]
    ]
    return InlineKeyboardMarkup(keyboard)


# Обработчик для показа категорий
async def show_categories(update, context):
    await update.callback_query.message.reply_text(
        "🪶🦚राधे राधे𓃔🦚\n\nВыберите категорию товаров:",
        reply_markup=create_category_keyboard()
    )


# Асинхронная функция для получения продуктов по бренду
@sync_to_async
def get_products_by_brand(brand_name):
    return Product.objects.filter(name__icontains=brand_name)


def motorcycle_options():
    # Создаем инлайн-кнопки для выбора категорий мотоциклов
    keyboard = [
        [InlineKeyboardButton("🇮🇳 Индийские марки", callback_data="motorcycle_indian")],
        [InlineKeyboardButton("🇪🇺 Европейские марки", callback_data="motorcycle_european")],
        [InlineKeyboardButton("🇯🇵 Японские марки", callback_data="motorcycle_japanese")],
        [InlineKeyboardButton("🇺🇸 Американские марки", callback_data="motorcycle_american")],
        [InlineKeyboardButton("🔙 Назад в магазин", callback_data="back_to_categories")]
    ]

    return InlineKeyboardMarkup(keyboard)


# Обработчик для показа категорий мотоциклов
async def category_motorcycle_options(update, context):
    await update.callback_query.message.reply_text(
        "🏍️ Выберите категорию мотоциклов:",
        reply_markup=motorcycle_options()
    )


async def show_motorcycle_options(update, context):
    query = update.callback_query
    await query.answer()  # Подтверждаем получение колбэка

    # Получаем все мотоциклы из базы данных
    motorcycle_products = await sync_to_async(Product.objects.filter)(category__name__iexact='Мотоциклы')

    keyboard = []

    for product in await sync_to_async(list)(motorcycle_products):
        keyboard.append([InlineKeyboardButton(product.name, callback_data=f"motorcycle_{product.slug}")])

    # Добавляем кнопку "Назад"
    keyboard.append([InlineKeyboardButton("🔙 Назад в магазин", callback_data="back_to_categories")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="🏍 Выберите мотоцикл:",
        reply_markup=reply_markup
    )


def incense_options():
    # Создаем инлайн-кнопки для выбора благовоний
    keyboard = [
        [InlineKeyboardButton("🥢 Индийские благовония", callback_data="aromo_indian")],
        [InlineKeyboardButton("🌿 Японские благовония", callback_data="incense_japanese")],
        [InlineKeyboardButton("🪔 Тибетские благовония", callback_data="incense_tibetan")],
        [InlineKeyboardButton("🌸 Ароматические палочки", callback_data="incense_sticks")],
        [InlineKeyboardButton("🔙 Назад в магазин", callback_data="back_to_categories")]
    ]

    return InlineKeyboardMarkup(keyboard)


# Обработчик для показа категорий
async def category_incense_options(update, context):
    await update.callback_query.message.reply_text(
        "🪶🦚राधे राधे𓃔🦚\n\nВыберите категорию благовоний:",
        reply_markup=incense_options()
    )


async def show_incense_options(update, context):
    query = update.callback_query
    await query.answer()  # Подтверждаем получение колбэка

    # Получаем все индийские благовония
    incense_products = await sync_to_async(Product.objects.filter)(category__name__iexact='Индийские благовония')

    keyboard = []

    for product in await sync_to_async(list)(incense_products):
        keyboard.append([InlineKeyboardButton(product.name, callback_data=f"incense_{product.slug}")])

    # Добавляем кнопку "Назад"
    keyboard.append([InlineKeyboardButton("🔙 Назад в магазин", callback_data="back_to_categories")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="🪔🦚🪷🐚🪕🦢\n\nВыберите благовоние:",
        reply_markup=reply_markup
    )

# Отображение кнопок для начала регистрации
keyboard = [
    [InlineKeyboardButton("Начать регистрацию", callback_data="start_registration")],
    [InlineKeyboardButton("Отменить регистрацию", callback_data="end_registration")],
]
reg_reply_markup = InlineKeyboardMarkup(keyboard)
