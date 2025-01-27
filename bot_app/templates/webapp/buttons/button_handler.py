import logging

from asgiref.sync import sync_to_async

from bot_app.models import UserRegistration
from bot_app.templates.webapp.buttons.inline_category_store_btn import show_categories, \
    show_incense_options, show_motorcycle_options, category_incense_options, category_motorcycle_options
from bot_app.templates.webapp.microns.moto_shows_products_brands import show_products_by_brand
from bot_app.templates.webapp.profile.registrations_store import registration_handler, STEP_EDIT_NAME
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
from telegram.ext import CallbackContext, ContextTypes, ConversationHandler

cart = Cart()


# Обработка инлайн-кнопок
async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    # Обработка кнопок редактирования и подтверждения данных
    if query.data == 'edit_data':
        await query.edit_message_text("✏️ Пожалуйста, введите ваши данные снова.")
        context.user_data['step'] = None  # Сброс шага регистрации
        await registration_handler(update, context)
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

    if query.data == "delete_item":
        await query.message.reply_text("Функция удаления товара пока не реализована.")
    elif query.data == "pay_item":
        await query.message.reply_text("Функция оплаты товара пока не реализована.")

    if query.data == "end_registration":
        await query.message.reply_text('🚧 Вы отменили регистрацию. ⛔ ', reply_markup=main_markup)
        # Удаляем инлайн-кнопки
        await query.edit_message_reply_markup(reply_markup=None)
        # Завершаем состояние ConversationHandler
        return ConversationHandler.END
    if query.data == "start_registration":
        await registration_handler(update, context)

    elif query.data == "category_motorcycles":
        await category_motorcycle_options(update, context)
    if query.data == "motorcycle_indian":
        await show_motorcycle_options(update, context)
    elif query.data == "back_to_categories":
        await show_categories(update, context)
    elif query.data.startswith("motorcycle_"):  # Проверяем, начинается ли колбэк с "motorcycle_"
        slug = query.data.split("_")[1]  # Извлекаем слаг
        logging.info(f"Запрос продукта с слагом: {slug}")  # Логируем слаг
        await show_products_by_brand(update, context, slug)  # Передаем слаг в функцию показа продукта

    elif query.data == "category_incense":
        await category_incense_options(update, context)
    if query.data == "aromo_indian":
        await show_incense_options(update, context)
    elif query.data.startswith("incense_"):  # Проверяем, начинается ли колбэк с "incense_"
        slug = query.data.split("_")[1]  # Извлекаем слаг
        logging.info(f"Запрос продукта с слагом: {slug}")  # Логируем слаг

        # Дополнительная проверка на корректность слага
        if not slug.isalnum():  # Проверяем, состоит ли слаг только из букв и цифр
            error_message = "🤷‍♂️ Неизвестный слаг. Попробуйте снова."
            try:
                await query.edit_message_text(error_message)
            except Exception as e:
                logging.error(f"Ошибка редактирования сообщения: {e}")
            return

        await show_products_by_brand(update, context, slug)  # Передаем слаг в функцию показа продуктов

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

    #     # Если ни одно из условий не выполнено, показываем сообщение об ошибке
    #
    # error_message = "🤷‍♂️ Привет я в баттон хендлере, Неизвестный выбор. Попробуйте снова."
    #
    # try:
    #
    #     await query.edit_message_text(error_message)
    #
    # except Exception as e:

        print(f"Error editing message: {e}")

    # Можно добавить лог для текущего количества, если нужно
    print(context.user_data["quantity"])


async def cancel_registration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    # Отвечаем на callback
    await query.answer()

    # Уведомляем пользователя об отмене регистрации
    await query.message.reply_text('🚧 Вы отменили регистрацию. ⛔', reply_markup=main_markup)

    # Удаляем инлайн-кнопки
    await query.edit_message_reply_markup(reply_markup=None)

    # Завершаем состояние ConversationHandler
    return ConversationHandler.END


async def edit_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    new_name = update.message.text

    try:
        print(f"Пользователь {user_id} ввел новое имя: {new_name}.")  # Логируем данные

        # Обновляем имя в базе данных
        await sync_to_async(UserRegistration.objects.filter(user_id=user_id).update)(name=new_name)

        await update.message.reply_text("Ваше имя успешно обновлено.")
        return ConversationHandler.END

    except Exception as e:
        print(f"Ошибка в edit_name_handler: {e}")  # Логируем ошибку
        await update.message.reply_text("Произошла ошибка. Попробуйте снова.")
        return ConversationHandler.END

