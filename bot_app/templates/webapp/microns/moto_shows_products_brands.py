import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot_app.models import Product
from bot_app.templates.webapp.buttons.buttons import create_reply_sklad_btn


from asgiref.sync import sync_to_async


async def show_products_by_brand(update, context, slug):
    query = update.callback_query
    await query.answer()  # Подтверждаем получение колбэка

    logging.info(f"Запрос продукта с слагом: {slug}")

    try:
        product = await sync_to_async(Product.objects.get)(slug=slug)
        logging.info(f"Найден продукт: {product.name}")
    except Product.DoesNotExist:
        logging.error(f"Продукт не найден для слага: {slug}")
        await query.message.reply_text("Продукт не найден.")
        return

    # Получаем категорию асинхронно
    category_name = 'Неизвестная категория'
    if await sync_to_async(product.category.exists)():
        category = await sync_to_async(product.category.first)()
        category_name = category.name if category else 'Неизвестная категория'

    product_list = (
        f"<b>Имя:</b> {product.name}\n"
        f"<b>Бренд:</b> {product.brand}\n"
        f"<b>Категория:</b> {category_name}\n"
        f"<b>Цена:</b> {product.price}₽\n"
        f"<b>Описание:</b> {product.desc}\n"
    )

    # Создание кнопок
    back_button = InlineKeyboardButton("🔙 Назад в магазин", callback_data="back_to_categories")

    # Кнопки для управления количеством
    quantity = context.user_data.get("quantity", 1)  # Получаем текущее количество или 1 по умолчанию
    sklad_btn = create_reply_sklad_btn(
        quantity)  # Предполагается, что эта функция возвращает кнопки для управления количеством

    # Отправляем фото с кнопками
    if product.image:  # Проверяем наличие изображения
        try:
            with open(product.image.path, 'rb') as photo:
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
        except Exception as e:
            logging.error(f"Ошибка при отправке фото: {e}")
            await query.message.reply_text("Не удалось отправить изображение.")
