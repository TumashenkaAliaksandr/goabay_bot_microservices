from bot_app.templates.registrations_store import store_registration_handler
from bot_app.templates.webapp.buttons.buttons import reply_markup_pay, back_button_go, \
    order_calculation_pay, back_button_cal, back_qw_answ_button_main, qw_answ_btn_main, \
    back_gifts_button_main, gifts_btn_main, create_reply_sklad_btn
from bot_app.templates.webapp.cart import Cart
from bot_app.templates.webapp.text_files_py_txt.calculator_info_pay import calculator_info
from bot_app.templates.webapp.text_files_py_txt.info_pay import payment_info
from bot_app.templates.webapp.text_files_py_txt.qwe_answ import qwe_answer_info
from bot_app.templates.webapp.text_files_py_txt.sales_info import sales_info
from telegram import Update
from bot_app.templates.webapp.buttons.buttons_store import *
from telegram.ext import CallbackContext


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

    # # Получение текущего количества
    # quantity = context.user_data["quantity"]

    # Обработка нажатия кнопок
    if query.data == "add_to_cart":
        # Получаем данные товара и количество
        product_id = context.user_data.get("product_id")  # Получаем product_id из user_data
        quantity = context.user_data.get("quantity", 1)  # Получаем текущее количество (по умолчанию 1)
        product_data = context.user_data.get("product")  # Получаем данные о товаре

        # Проверяем, что данные о товаре существуют
        if not product_data:
            await query.answer("Ошибка: не найден товар. Попробуйте снова.")
            return

        # Проверяем, что название товара есть в данных
        product_name = product_data.get("name")
        if not product_name:
            await query.answer("Ошибка: у товара отсутствует название.")
            return

        # Добавляем товар в корзину
        cart.add_item(quantity, product_data)

        # Отправляем всплывающее сообщение о добавлении в корзину
        await query.answer(f"Товар '{product_name}' добавлен в корзину: {quantity} шт.")

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
    