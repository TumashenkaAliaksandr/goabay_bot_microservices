import asyncio
import logging

from telegram import Update
from telegram.ext import CallbackContext

from bot_app.templates.webapp.answers.answer_money import get_currency_rates
from bot_app.templates.webapp.answers.info_back import messages_to_delete
from bot_app.templates.webapp.buttons.button_handler import cart
from bot_app.templates.webapp.buttons.buttons import reply_markup_pay, offerta_button, \
    order_calculation_pay, qw_answ_btn_main, track_button, \
    gifts_btn_main, create_reply_sklad_btn, create_cart_keyboard, manger_button
from bot_app.templates.webapp.buttons.buttons_how_working import goa_pay_btn, delivery_btn, warehouse_btn, pays_btn
from bot_app.templates.webapp.buttons.buttons_store import *
from bot_app.templates.webapp.buttons.inline_category_store_btn import create_category_keyboard
from bot_app.templates.webapp.microns.screens import escape_markdown_v2
from bot_app.send_rabbitmq import send_to_rabbitmq
from bot_app.templates.webapp.parcer import fetch_product_data
from bot_app.templates.webapp.text_files_py_txt.anager_answer import manager_info
from bot_app.templates.webapp.text_files_py_txt.delivery import delivery_info
from bot_app.templates.webapp.text_files_py_txt.warehouse_info import warehouse_info


# Функция для удаления сообщения через минуту
async def delete_message(context: CallbackContext):
    job = context.job
    try:
        # Удаляем сообщение по message_id, который хранится в job.context
        await job.context.delete()
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения: {e}")


# Основная функция для обработки сообщений
async def echo(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    send_to_rabbitmq(message)

    # Удаление старого сообщения пользователя через 0.1 секунды
    await asyncio.sleep(0.1)
    try:
        await update.message.delete()  # Удаляем исходное сообщение пользователя
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения: {e}")

    if message == "Товары из Индии 👳‍♀️":
        # Отправляем сообщение о выборе
        response_message = await update.message.reply_text('Вы выбрали "Товары из Индии 👳‍♀️".')
        messages_to_delete.append(response_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_two = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=products_btn_india
        )
        messages_to_delete.append(get_back_two)  # Добавляем в список для удаления

    elif message == "Как мы работаем 🛠":
        res_message = await update.message.reply_text('Вы выбрали "Как мы работаем 🛠".')
        messages_to_delete.append(res_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_job = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=how_we_work_btn
        )
        messages_to_delete.append(get_back_job)  # Добавляем в список для удаления

    elif message == "Сервис 🔧":
        serv_res_message = await update.message.reply_text('Вы выбрали "Сервис 🔧".')
        messages_to_delete.append(serv_res_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_serv = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=service_btn
        )
        messages_to_delete.append(get_back_serv)  # Добавляем в список для удаления

    elif message == "О компании 🏢":
        about_res_message = await update.message.reply_text('Вы выбрали "О компании 🏢".')
        messages_to_delete.append(about_res_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_about = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=about_btn
        )
        messages_to_delete.append(get_back_about)  # Добавляем в список для удаления

    elif message == "Наш Блог 📚":
        blog_res_message = await update.message.reply_text('Вы выбрали "Наш Блог 📚".')
        messages_to_delete.append(blog_res_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        our_get_back = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=blog_btn
        )
        messages_to_delete.append(our_get_back)  # Добавляем в список для удаления

    elif message == "💳 Оплата":
        pay_res_message = await update.message.reply_text('👳‍♂️ Оплата индийских товаров и услуг')
        messages_to_delete.append(pay_res_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        pay_get_back = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=goa_pay_btn
        )
        messages_to_delete.append(pay_get_back)  # Добавляем в список для удаления

    elif message == "🏪 Склад В Индии":
        await update.message.reply_text('Вы перешли в раздел - 🏪 Склад В Индии', reply_markup=warehouse_btn)

    elif message == "⬅️":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)
            except Exception as e:
                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления
        messages_to_delete.clear()

        # Отправляем сообщение о возврате в главное меню
        await update.message.reply_text('Вы вернулись в "Главное меню 🍳".', reply_markup=main_markup)

    elif message == "⬅️ Назад к информации":  # Новая кнопка для возврата к информации

        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:

            try:

                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()

        # Отправляем сообщение о возврате к информации с соответствующей клавиатурой

        back_to_job = await update.message.reply_text('Вы вернулись в "Как мы работаем 🛠".')
        messages_to_delete.append(back_to_job)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        pay_get_back = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=how_we_work_btn
        )
        messages_to_delete.append(pay_get_back)  # Добавляем в список для удаления

    elif message == "⬅️ Товары из Индии":
        await update.message.reply_text('Вы вернулись в Товары из Индии 👳‍♀️', reply_markup=products_btn_india)
    elif message == "⬅️ Как мы работаем 🛠":
        await update.message.reply_text('Вы вернулись в Как мы работаем 🛠', reply_markup=how_we_work_btn)
    elif message == "Способы оплаты 🏧":
        await update.message.reply_text('💰 Оплата индийских товаров и услуг доступна только по безналичному расчету.\n\n'
                                        '📧 Мы выставим счет по электронной почте.\n👇 🏧 Способы оплаты', reply_markup=reply_markup_pay)
    elif message == "Расчет заказа 💰":
        await update.message.reply_text('📊 Расчет заказа индийских товаров.\n\n'
                                        '📧 Мы выставим счет по электронной почте.\n👇 🧮 Расчет заказа', reply_markup=order_calculation_pay)
    elif message == '💸 Курс валют':
        await get_currency_rates(update, context)
    elif message == '📊 Экономика':
        await update.message.reply_text('Вы выбрали "📊 Экономика".', reply_markup=how_economic_btn)
    elif message == "🚚 Доставка":
        await update.message.reply_text('Вы выбрали "🚚 Доставка".', reply_markup=delivery_btn)
    elif message == "📝 Информация о Доставке":
        await update.message.reply_text(delivery_info, parse_mode='MarkdownV2')
    elif message == "🏗 Как работает Склад":
        await update.message.reply_text(warehouse_info, parse_mode='MarkdownV2')
    elif message == "🚨 Помощь":
        await update.message.reply_text('Вы выбрали "🚨 Помощь".', reply_markup=helps_btn)
    elif message == "👳‍♂️ Написать обращение":
        await update.message.reply_text(manager_info, parse_mode='MarkdownV2', reply_markup=manger_button)

    elif message == "🛒 Мои Покупки":
        await update.message.reply_text('Вы перешли в 🛒 Мои Покупки', reply_markup=pays_btn)

    if message == "🛒":
        cart_items = cart.get_cart_items()  # Получаем элементы из корзины
        if not cart_items:
            await update.message.reply_text("Ваша корзина пуста.")
        else:
            # Формируем сообщение с содержимым корзины
            purchases_info = "📌 Ваши Заказы:\n\n"
            for product_data, quantity in cart_items.items():
                # Извлекаем данные о товаре
                name = quantity.get('name', 'Неизвестный товар')
                # description = quantity.get('description', 'Описание отсутствует')
                price = quantity.get('price', {})
                current_price = price.get('current', 'Уточнить цену')
                # image_url = quantity.get('image', None)
                product_url = context.user_data.get('product_url', 'Не получилось')

                # Формируем информацию о товаре
                product_info = f"🎁 Товар: {name}\n〰️〰️〰️\n" \
                               f"🔢 Количество: {product_data}\n〰️〰️〰️\n" \
                               f"💰 Цена: {current_price}\n〰️〰️〰️\n"\
                               f"🔗 Ссылка на товар: {product_url}\n〰️〰️〰️\n"\
                               f"💸 *Итог: {current_price}\n"
                # f"📝 Описание: {description}\n"

                # Добавляем изображение товара, если оно есть
                # if image_url:
                #     product_info += f"\n![Изображение товара]\n({image_url})"

                # Добавляем товар в список заказов
                purchases_info += f"\n{product_info}\n{'-' * 30}\n"

            # Экранируем сообщение перед отправкой
            purchases_info = escape_markdown_v2(purchases_info)

            await update.message.reply_text(
                purchases_info,
                parse_mode='MarkdownV2',
                reply_markup=create_cart_keyboard()
            )

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
    elif message in ["👤", "Личный кабинет 👤"]:
        await update.message.reply_text('Вы вернулись в кабинет 👤', reply_markup=profile_btn)
    elif message == "🔙 Назад в кабинет":
        await update.message.reply_text('Вы вернулись в кабинет 👤', reply_markup=profile_btn)
    elif message == "📁 Каталог":
        await update.message.reply_text('🪶🦚राधे राधे𓃔🦚\n\n📍 Вы выбрали 📁 Каталог \n🗃 Выбирите категорию товара 👇\n〰️〰️〰️', reply_markup=create_category_keyboard())
    elif message == "🏪 Магазин":
        await update.message.reply_text('Вы выбрали 🏪 Магазин', reply_markup=catalog_btn)
        # Запрос ссылки на товар
    if message == "🔗 Ввести ссылку Goabay":
        await update.message.reply_text("🔗 Введите ссылку https:// 👇 на Товар 🛍️ магазина 🏝GoaBay.com ")
    elif message == "🛍 Товары на складе":
        await update.message.reply_text(
            '🪶🦚राधे राधे𓃔🦚\n\n📍 Вы выбрали 🛍 Товары на складе \n🗃 Выбирите категорию товара 👇\n〰️〰️〰️',
            reply_markup=create_category_keyboard())

        # Обработка ссылки на товар
    elif message.startswith("http://") or message.startswith("https://"):
        context.user_data['product_url'] = message
        product_data = fetch_product_data(message)

        if "error" in product_data:
            await update.message.reply_text(product_data["error"])
            return


        # Формирование текста ответа
        reply_text = (
            f"*Имя:* {product_data.get('name', 'Не найдено')}\n"
            f"*Описание:* {product_data.get('description', 'Не найдено')}\n"
            f"*Цена:* {product_data.get('price', {}).get('current', 'Соглосовать цену')} "
            f"(Цена без скидки: {product_data.get('price', {}).get('original', 'Не указана')})\n"
            f"*Ссылка на товар:* {context.user_data['product_url']}\n"
        )

        # Получаем текущее количество из user_data или устанавливаем 1 по умолчанию
        quantity = context.user_data.get("quantity", 1)
        # Сохранение данных продукта в user_data
        context.user_data['product'] = product_data

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


