from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot_app.templates.webapp.buttons.button_handler import cart

from bot_app.templates.webapp.buttons.buttons import create_cart_keyboard
from bot_app.templates.webapp.microns.screens import escape_markdown_v2


async def handle_cart(update, context):
    message = update.message.text

    if message == "🛒":
        cart_items = cart.get_cart_items()  # Получаем элементы из корзины
        if not cart_items:
            await update.message.reply_text("Ваша корзина пуста.")
        else:
            # Формируем сообщение с содержимым корзины
            purchases_info = "📌 Ваши Заказы:\n\n"
            for product_id, quantity in cart_items.items():
                # Извлекаем данные о товаре из user_data
                product_data = context.user_data.get("product", {}).get(product_id, {})
                name = product_data.get("name", 'Неизвестный товар')
                price = product_data.get("price", {})
                current_price = price.get("current", 'Уточнить цену')
                product_url = product_data.get("url", 'Не получилось')

                # Формируем информацию о товаре
                product_info = (
                    f"🎁 Товар: {name}\n"
                    f"🔢 Количество: {quantity}\n"
                    f"💰 Цена: {current_price}\n"
                    f"🔗 Ссылка на товар: {product_url}\n"
                    f"💸 *Итог: {current_price * quantity}*\n"
                )

                # Добавляем товар в список заказов
                purchases_info += f"\n{product_info}\n{'-' * 30}\n"

            # Экранируем сообщение перед отправкой
            purchases_info = escape_markdown_v2(purchases_info)

            await update.message.reply_text(
                purchases_info,
                parse_mode='MarkdownV2',
                reply_markup=create_cart_keyboard()  # Добавьте вашу клавиатуру для управления корзиной
            )
