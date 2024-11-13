from telegram import InlineKeyboardButton, InlineKeyboardMarkup


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


# Пример использования:
async def show_categories(update, context):
    await update.message.reply_text(
        "🪶🦚राधे राधे𓃔🦚\n\nВыберите категорию товаров:",
        reply_markup=create_category_keyboard()
    )
