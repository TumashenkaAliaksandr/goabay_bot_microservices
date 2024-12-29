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


def create_motorcycle_brands_keyboard():
    keyboard = [
        [InlineKeyboardButton("Hero MotoCorp", callback_data="brand_hero")],
        [InlineKeyboardButton("Bajaj Moto", callback_data="brand_bajaj")],
        [InlineKeyboardButton("TVS Motor Company", callback_data="brand_tvs")],
        [InlineKeyboardButton("Royal Enfield", callback_data="brand_royal_enfield")],
        [InlineKeyboardButton("KTM India", callback_data="brand_ktm")],
        [InlineKeyboardButton("🔙 Назад к категориям", callback_data="back_to_categories")]
    ]
    return InlineKeyboardMarkup(keyboard)


def incense_options():
    # Создаем инлайн-кнопки для выбора благовоний
    keyboard = [
        [InlineKeyboardButton("🥢 Индийские благовония", callback_data="incense_indian")],
        [InlineKeyboardButton("🌿 Японские благовония", callback_data="incense_japanese")],
        [InlineKeyboardButton("🪔 Тибетские благовония", callback_data="incense_tibetan")],
        [InlineKeyboardButton("🌸 Ароматические палочки", callback_data="incense_sticks")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories")]
    ]

    return InlineKeyboardMarkup(keyboard)


# Асинхронная функция для получения продуктов по бренду
@sync_to_async
def get_products_by_brand(brand_name):
    return Product.objects.filter(name__icontains=brand_name)


# Обработчик для показа категорий
async def show_categories(update, context):
    await update.callback_query.message.reply_text(
        "🪶🦚राधे राधे𓃔🦚\n\nВыберите категорию товаров:",
        reply_markup=create_category_keyboard()
    )


# Обработчик для показа марок мотоциклов
async def show_motorcycle_brands(update, context):
    await update.callback_query.message.reply_text(
        "🏍 Выберите марку мотоцикла:",
        reply_markup=create_motorcycle_brands_keyboard()
    )


async def show_incense_options(update, context):
    await update.callback_query.message.reply_text(
        # "🪶🦚राधे राधे𓃔🦚\n\n"
        "🪔🦚🪷🐚🪕🦢\n\n"
        "Выберите Благовония:",
        reply_markup=incense_options()
    )
