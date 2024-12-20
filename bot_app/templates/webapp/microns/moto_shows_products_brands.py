from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot_app.models import Product
from bot_app.templates.webapp.buttons.buttons import create_reply_sklad_btn
from bot_app.templates.webapp.buttons.inline_category_store_btn import show_motorcycle_brands


async def show_products_by_brand(update, context):
    query = update.callback_query
    await query.answer()  # Подтверждаем получение колбэка

    brand_mapping = {
        "brand_hero": "Hero MotoCorp",
        "brand_bajaj": "Bajaj Moto",
        "brand_tvs": "TVS Motor Company",
        "brand_royal_enfield": "Royal Enfield",
        "brand_ktm": "KTM India"
    }

    brand_name = brand_mapping.get(query.data)

    if brand_name:
        # Получаем продукты асинхронно
        products = await sync_to_async(Product.objects.filter)(brand__iexact=brand_name)

        if await sync_to_async(products.exists)():  # Проверяем наличие продуктов
            product_list = ""
            for product in await sync_to_async(list)(products):  # Преобразуем QuerySet в список асинхронно
                product_list += (
                    f"<b>Имя:</b> {product.name}\n"
                    f"<b>Бренд:</b> {product.brand}\n"
                    f"<b>Категория:</b> {product.category}\n"
                    f"<b>Цена:</b> {product.price}₽\n"
                    f"<b>Описание:</b> {product.desc}\n"
                )

                # Создаем кнопки для управления количеством и добавления в корзину
                quantity = 1  # Здесь можно задать начальное количество, например, 1
                sklad_btn = create_reply_sklad_btn(quantity)

                # Отправляем фото
                if product.image:  # Проверяем наличие изображения
                    with open(product.image.path, 'rb') as photo:
                        # Создаем кнопку "Назад к брендам"
                        back_button = InlineKeyboardButton("🔙 Назад к брендам", callback_data="back_to_brands")
                        back_keyboard = InlineKeyboardMarkup([[back_button]])

                        await context.bot.send_photo(
                            chat_id=query.message.chat.id,
                            photo=photo,
                            caption=product_list,
                            parse_mode='HTML',  # Используем HTML для форматирования
                            reply_markup=InlineKeyboardMarkup([
                                [back_button],  # Кнопка назад
                                *sklad_btn.inline_keyboard  # Добавляем кнопки управления количеством из sklad_btn
                            ])
                        )
        else:
            await query.message.reply_text(f"Нет доступных продуктов для марки *{brand_name}*.")
    else:
        await query.message.reply_text("Неизвестный бренд.")


