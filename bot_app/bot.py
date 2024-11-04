import os

import django

from bot_app.templates.webapp.answers.answer_money import get_currency_rates
from bot_app.templates.webapp.buttons.buttons import reply_markup_pay, back_button_go, offerta_button, \
    order_calculation_pay, back_button_cal, back_qw_answ_button_main, qw_answ_btn_main, track_button, \
    back_gifts_button_main, gifts_btn_main, create_reply_sklad_btn
from bot_app.templates.webapp.buttons.buttons_how_working import goa_pay_btn, delivery_btn, warehouse_btn
from bot_app.templates.webapp.cart import Cart
from bot_app.templates.webapp.microns.commands import start, help
from bot_app.templates.webapp.microns.screens import escape_markdown_v2
from bot_app.templates.webapp.microns.send_rabbitmq import send_to_rabbitmq
from bot_app.templates.webapp.parcer import fetch_product_data
from bot_app.templates.webapp.text_files_py_txt.calculator_info_pay import calculator_info
from bot_app.templates.webapp.text_files_py_txt.delivery import delivery_info
from bot_app.templates.webapp.text_files_py_txt.info_pay import payment_info
from bot_app.templates.webapp.text_files_py_txt.qwe_answ import qwe_answer_info
from bot_app.templates.webapp.text_files_py_txt.sales_info import sales_info
from bot_app.templates.webapp.text_files_py_txt.warehouse_info import warehouse_info

# Настройка окружения и Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goabay_bot.settings')
django.setup()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, filters
from telegram.ext import CallbackQueryHandler
from django.conf import settings
from bot_app.templates.profile_date import profile_button_handler
from bot_app.templates.webapp.buttons.buttons_store import *
from bot_app.templates.registrations_store import store_registration_handler
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Основная функция для обработки сообщений
async def echo(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    send_to_rabbitmq(message)

    if message == "Товары из Индии 👳‍♀️":
        await update.message.reply_text('Вы выбрали "Товары из Индии 👳‍♀️".', reply_markup=products_btn_india)
    elif message == "Как мы работаем ⌚️":
        await update.message.reply_text('Вы выбрали "Как мы работаем ⌚️".', reply_markup=how_we_work_btn)
    elif message == "Сервис 🔧":
        await update.message.reply_text('Вы выбрали "Сервис 🔧".', reply_markup=service_btn)
    elif message == "О компании 🏢":
        await update.message.reply_text('Вы выбрали "О компании 🏢".', reply_markup=about_btn)
    elif message == "Наш Блог 📚":
        await update.message.reply_text('Вы выбрали "Наш Блог 📚".', reply_markup=blog_btn)
    elif message == "💳 Оплата":
        await update.message.reply_text('👳‍♂️ Оплата индийских товаров и услуг', reply_markup=goa_pay_btn)
    elif message == "🏪 Склад В Индии":
        await update.message.reply_text('Вы перешли в раздел - 🏪 Склад В Индии', reply_markup=warehouse_btn)
    elif message == "⬅️ Назад":
        await update.message.reply_text('Вы вернулись в "Главное меню 🍳".', reply_markup=main_markup)
    elif message == "⬅️ Назад к информации":
        await update.message.reply_text('Вы вернулись в "Как мы работаем ⌚️".', reply_markup=how_we_work_btn)
    elif message == "⬅️ Товары из Индии":
        await update.message.reply_text('Вы вернулись в Товары из Индии 👳‍♀️".', reply_markup=products_btn_india)
    elif message == "Способы оплаты 🏧":
        await update.message.reply_text('💰 Оплата индийских товаров и услуг доступна только по безналичному расчету.\n\n'
                                        '📧 Мы выставим счет по электронной почте.\n👇 🏧 Способы оплаты', reply_markup=reply_markup_pay)
    elif message == "Расчет заказа 💰":
        await update.message.reply_text('📊 Расчет заказа индийских товаров.\n\n'
                                        '📧 Мы выставим счет по электронной почте.\n👇 🧮 Расчет заказа', reply_markup=order_calculation_pay)
    elif message == "Как мы работаем ⌛️️":
        await update.message.reply_text('Вы выбрали "Как мы работаем ⌛️️".', reply_markup=how_we_work_btn)
    elif message == '💸 Курс валют':
        await get_currency_rates(update, context)
    elif message == "🚚 Доставка":
        await update.message.reply_text('Вы выбрали "🚚 Доставка".', reply_markup=delivery_btn)
    elif message == "📝 Информация о Доставке":
        await update.message.reply_text(delivery_info, parse_mode='MarkdownV2')
    elif message == "🏗 Как работает Склад":
        await update.message.reply_text(warehouse_info, parse_mode='MarkdownV2')
        # Предположим, что у вас уже есть класс Cart с методами get_cart_items
    if message == "🛒 Мои Покупки":
        cart_items = cart.get_cart_items()  # Получаем элементы из корзины
        if not cart_items:
            await update.message.reply_text("Ваша корзина пуста.")
        else:
            # Формируем сообщение с содержимым корзины
            purchases_info = "Ваши покупки:\n"
            for product_id, quantity in cart_items.items():
                purchases_info += f"- Товар ID: {product_id}, Количество: {quantity}\n"

            # Экранируем сообщение перед отправкой
            purchases_info = escape_markdown_v2(purchases_info)

            await update.message.reply_text(purchases_info, parse_mode='MarkdownV2')

    elif message == "🗣 ЧаВо":
        await update.message.reply_text('⁉️ Вопрос-Ответ.\n\n'
                                       '👇 Сделайте выбор что вас интересует.', reply_markup=qw_answ_btn_main)
        # Добавляем кнопку для публичной оферты
    elif message == "Публичная оферта 📜":
        await update.message.reply_text("📎 👇 Нажмите на кнопку ниже для перехода:", reply_markup=offerta_button)
    elif message == "👀 Отследить заказ":
        await update.message.reply_text("📎 👇 Нажмите на кнопку ниже для перехода:", reply_markup=track_button)
    elif message == "🎁 Подарки":
        await update.message.reply_text("Вы выбрали 🎁 Подарки", reply_markup=gifts_btn_main)
    elif message == "🔙 Назад в кабинет":
        await update.message.reply_text('Вы вернулись в кабинет 👤', reply_markup=profile_btn)
        # Запрос ссылки на товар
    if message == "🛍 Товары на складе":
        await update.message.reply_text("Введите ссылку 🔗 на Товар 🛍")

        # Обработка ссылки на товар
    elif message.startswith("http://") or message.startswith("https://"):
        product_data = fetch_product_data(message)

        if "error" in product_data:
            await update.message.reply_text(product_data["error"])
            return

        # Формирование текста ответа
        reply_text = (
            f"*Имя:* {product_data.get('name', 'Не найдено')}\n"
            f"*Описание:* {product_data.get('description', 'Не найдено')}\n"
            f"*Цена:* {product_data.get('price', {}).get('current', 'Не указана')} "
            f"(Цена без скидки: {product_data.get('price', {}).get('original', 'Не указана')})\n"
        )

        # Получаем текущее количество из user_data или устанавливаем 1 по умолчанию
        quantity = context.user_data.get("quantity", 1)

        # Проверка наличия изображения и отправка сообщения с кнопками
        if 'image' in product_data:
            await update.message.reply_photo(
                photo=product_data['image'],
                caption=reply_text,
                parse_mode="Markdown",
                reply_markup=create_reply_sklad_btn(quantity)  # Подключение инлайн-кнопок
            )
        else:
            await update.message.reply_text(
                reply_text,
                parse_mode="Markdown",
                reply_markup=create_reply_sklad_btn(quantity)  # Подключение инлайн-кнопок
            )


            # Обработка других сообщений
    # else:
    #     await update.message.reply_text(
    #             "Пожалуйста, введите корректную ссылку на товар или выберите опцию 🛍 Товары на складе.")

    # if message == "Личный кабинет 👤":
    #     # Проверяем регистрацию и вызываем соответствующий обработчик
    #     user_id = update.message.from_user.id
    #     registration = await sync_to_async(UserRegistration.objects.filter)(user_id=user_id).first()
    #
    #     if registration and registration.name and registration.email and registration.phone:
    #         # Пользователь зарегистрирован, показываем личный кабинет
    #         await show_user_info(update, context)
    #     else:
    #         # Пользователь не зарегистрирован, запускаем регистрацию
    #         await store_registration_handler(update, context)
    #
    # elif message == "✏️ Редактировать данные":
    #     await store_registration_handler(update, context)
# Инициализация корзины
cart = Cart()

# Обработка инлайн-кнопок
async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    # Обработка кнопок редактирования и подтверждения данных
    if query.data == 'edit_data':
        await query.edit_message_text("✏️ Пожалуйста, введите ваши данные снова.")
        context.user_data['step'] = None  # Сброс шага регистрации
        await store_registration_handler(update, context)
        return

    elif query.data == 'confirm_data':
        await query.edit_message_text("✔️ Ваши данные подтверждены!")
        await query.edit_message_text('Главное меню: 🍳', reply_markup=profile_btn)
        context.user_data.clear()
        return

    payment_method = query.data

    if payment_method in payment_info:
        text, photo_path = payment_info[payment_method]
        with open(photo_path, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=query.message.chat.id,
                photo=photo,
                caption=text,
                parse_mode='MarkdownV2',
                reply_markup=back_button_go  # Кнопка "Назад"
            )
        return

    elif query.data == 'back_pay':
        # Возвращаем пользователя к выбору способа оплаты
        await query.message.reply_text("💰 Оплата индийских товаров и услуг доступна только по безналичному расчету.\n\n"
                                       "📧 Мы выставим счет по электронной почте.\n👇 🏧 Cпособы оплаты:", reply_markup=reply_markup_pay)
        return

    # калькулятор методы
    calculator_method = query.data

    if calculator_method in calculator_info:
        text, photo_path = calculator_info[calculator_method]
        with open(photo_path, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=query.message.chat.id,
                photo=photo,
                caption=text,
                parse_mode='MarkdownV2',
                reply_markup=back_button_cal  # Кнопка "Назад"
            )
        return

    elif query.data == 'back_calculator':
        # Возвращаем пользователя к выбору шагов калькулятора
        await query.message.reply_text('📊 Расчет заказа индийских товаров.\n\n'
                                        '📧 Мы выставим счет по электронной почте.\n👇 🧮 Расчет заказа',
                                        reply_markup=order_calculation_pay)
        return

    # вопрос ответ
    qwe_answer_method = query.data

    if qwe_answer_method in qwe_answer_info:
        text, photo_path = qwe_answer_info[qwe_answer_method]
        with open(photo_path, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=query.message.chat.id,
                photo=photo,
                caption=text,
                parse_mode='MarkdownV2',
                reply_markup=back_qw_answ_button_main # Кнопка "Назад"
            )
        return

    elif query.data == 'back_qwe_answer':
        # Возвращаем пользователя к выбору шагов калькулятора
        await query.message.reply_text('⁉️ Вопрос-Ответ.\n\n'
                                       '👇 Сделайте выбор что вас интересует.',
                                       reply_markup=qw_answ_btn_main)
        return

        # Акции
    gifts_method = query.data

    if gifts_method in sales_info:
        print(sales_info[gifts_method])
        text, photo_path = sales_info[gifts_method]
        with open(photo_path, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=query.message.chat.id,
                photo=photo,
                caption=text,
                parse_mode='MarkdownV2',
                reply_markup=back_gifts_button_main  # Кнопка "Назад"
            )
        return

    elif query.data == 'back_gifts':
        # Возвращаем пользователя к выбору 🎁 Подарки
        await query.message.reply_text('🎁 Подарки\n\n'
                                       '👇 Сделайте выбор что вас интересует.',
                                       reply_markup=gifts_btn_main)
        return

    else:
        error_message = "🤷‍♂️ Неизвестный выбор. Попробуйте снова."
        try:
            await query.edit_message_text(error_message)
        except Exception as e:
            print(f"Error editing message: {e}")  # Логируем ошибку

    # Инициализация количества, если его нет в user_data
    if "quantity" not in context.user_data:
        context.user_data["quantity"] = 1

    # Получение текущего количества
    quantity = context.user_data["quantity"]

    # Обработка нажатия кнопок
    if query.data == "add_to_cart":
        product_id = context.user_data.get("product_id")  # Получаем product_id из user_data
        quantity = context.user_data.get("quantity", 1)  # Получаем текущее количество

        # Добавляем товар в корзину
        cart.add_item(product_id, quantity)

        # Отправляем всплывающее сообщение о добавлении в корзину
        await query.answer(f"Товар добавлен в корзину: {quantity} шт.")

    elif query.data == "increase_quantity":
        context.user_data["quantity"] += 1
        if query.message:  # Проверяем, что сообщение существует
            try:
                await query.edit_message_reply_markup(
                    reply_markup=create_reply_sklad_btn(context.user_data["quantity"]))
            except Exception as e:
                print(f"Error editing message: {e}")  # Логируем ошибку, если она возникла

    elif query.data == "decrease_quantity":
        if context.user_data["quantity"] > 1:  # Чтобы количество не становилось меньше 1
            context.user_data["quantity"] -= 1
            if query.message:  # Проверяем, что сообщение существует
                try:
                    await query.edit_message_reply_markup(
                        reply_markup=create_reply_sklad_btn(context.user_data["quantity"]))
                except Exception as e:
                    print(f"Error editing message: {e}")  # Логируем ошибку, если она возникла

    # Можно добавить лог для текущего количества, если нужно
    print(context.user_data["quantity"])


# Основная функция для запуска бота
def main() -> None:
    application = Application.builder().token(settings.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))

    # ConversationHandler для регистрации в магазине
    store_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & filters.Regex("^(Личный кабинет 👤)$"), store_registration_handler),
            MessageHandler(filters.TEXT & filters.Regex("^(✏️ Редактировать данные)$"), store_registration_handler)
        ],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_registration_handler)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_registration_handler)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_registration_handler)],
        },
        fallbacks=[],
    )

    application.add_handler(store_conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("👳‍♂️ Мои данные"), profile_button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()


if __name__ == '__main__':
    main()
