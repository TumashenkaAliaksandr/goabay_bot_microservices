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
from bot_app.templates.webapp.microns.turism_parser import get_tourism_articles_selenium
from bot_app.templates.webapp.parcer import fetch_product_data
from bot_app.templates.webapp.text_files_py_txt.anager_answer import manager_info
from bot_app.templates.webapp.text_files_py_txt.avia_answer import avia_answer_txt
from bot_app.templates.webapp.text_files_py_txt.delivery import delivery_info
from bot_app.templates.webapp.text_files_py_txt.hotel_answer import hotel_answer_txt
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
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        # Отправляем сообщение о выборе
        response_message = await update.message.reply_text('Вы выбрали "Товары из Индии 👳‍♀️".', reply_markup=None)
        messages_to_delete.append(response_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_two = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=products_btn_india
        )
        messages_to_delete.append(get_back_two)  # Добавляем в список для удаления

    elif message == "Как мы работаем 🛠":

        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()

        res_message = await update.message.reply_text('Вы выбрали "Как мы работаем 🛠".', reply_markup=None)
        messages_to_delete.append(res_message)  # Добавляем в список для удаления


        # Отправляем только клавиатуру с минимальным текстом
        get_back_job = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = '🙌 Выберите что вас интересует:',
            reply_markup=how_we_work_btn
        )
        messages_to_delete.append(get_back_job)  # Добавляем в список для удаления

    elif message == "Сервис 🔧":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        serv_res_message = await update.message.reply_text('Вы выбрали "Сервис 🔧".', reply_markup=None)
        messages_to_delete.append(serv_res_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_serv = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=service_btn
        )
        messages_to_delete.append(get_back_serv)  # Добавляем в список для удаления

    elif message == "🔙 Назад в сервис":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        back_service_message = await update.message.reply_text('Вы вернулись в Сервис 🔧', reply_markup=None)
        messages_to_delete.append(back_service_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_service = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=service_btn
        )
        messages_to_delete.append(get_back_service)  # Добавляем в список для удаления

    elif message == "О компании 🏢":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        about_res_message = await update.message.reply_text('Вы выбрали "О компании 🏢".', reply_markup=None)
        messages_to_delete.append(about_res_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_about = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=about_btn
        )
        messages_to_delete.append(get_back_about)  # Добавляем в список для удаления

    elif message == "Наш Блог 📚":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        blog_res_message = await update.message.reply_text('Вы выбрали "Наш Блог 📚".', reply_markup=None)
        messages_to_delete.append(blog_res_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        our_get_back = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=blog_btn
        )
        messages_to_delete.append(our_get_back)  # Добавляем в список для удаления

    elif message == "💳 Оплата":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        pay_res_message = await update.message.reply_text('👳‍♂️ Оплата индийских товаров и услуг', reply_markup=None)
        messages_to_delete.append(pay_res_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        pay_get_back = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=goa_pay_btn
        )
        messages_to_delete.append(pay_get_back)  # Добавляем в список для удаления

    elif message == "🏪 Склад В Индии":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        warehouse_res_message = await update.message.reply_text('Вы перешли в раздел - 🏪 Склад В Индии', reply_markup=None)
        messages_to_delete.append(warehouse_res_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_warehouse = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=warehouse_btn
        )
        messages_to_delete.append(get_back_warehouse)  # Добавляем в список для удаления

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
        main_menu_clear = await update.message.reply_text('Вы вернулись в "Главное меню 🍳".', reply_markup=None)
        messages_to_delete.append(main_menu_clear)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        menu_get_back = await update.message.reply_text(
            '👋 | WELCOME',
            reply_markup=main_markup
        )
        messages_to_delete.append(menu_get_back)  # Добавляем в список для удаления

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

        back_to_job = await update.message.reply_text('Вы вернулись в "Как мы работаем 🛠".', reply_markup=None)
        messages_to_delete.append(back_to_job)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        pay_get_back = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=how_we_work_btn
        )
        messages_to_delete.append(pay_get_back)  # Добавляем в список для удаления


    elif message == "🧗‍♀️ Туризм":

        # Удаляем все сообщения из списка, если они были отправлены ранее

        for msg in messages_to_delete:

            try:

                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()

        # Отправляем сообщение о начале загрузки статей

        back_to_india = await update.message.reply_text(

            '🔄 Открываю сайт: https://goabay.com/ пожалуйста подождите..\nМы предложим вам последних пять статей на выбор.',

            reply_markup=None

        )

        messages_to_delete.append(back_to_india)

        # Загружаем статьи

        articles = get_tourism_articles_selenium()

        if not articles or not isinstance(articles, list):  # Проверка, если список пустой или не является списком

            await update.message.reply_text("Статьи не найдены.")

            return

        if isinstance(articles, list) and isinstance(articles[0], dict) and "error" in articles[0]:
            await update.message.reply_text(articles[0]["error"])

            return

        # Формируем единое сообщение со всеми статьями

        articles_text = "📰 *Вот 5 последних статей о туризме:*\n\n"

        for article in articles:
            title = article.get("title", "Название отсутствует")

            date = article.get("date", "Дата неизвестна")

            link = article.get("link", "Ссылка недоступна")

            articles_text += f"📌 *{title}*\n➖➖➖\n🗓️ {date}\n➖➖➖\n🔗 [Читать статью]({link})\n\n﹌﹌﹌﹌﹌\n"

        # Отправляем все статьи одним сообщением

        msg = await update.message.reply_text(

            articles_text, parse_mode="Markdown", disable_web_page_preview=True

        )

        messages_to_delete.append(msg)

        # Отправляем клавиатуру

        india_get_back = await update.message.reply_text(

            '🙌 Выберите, что вас интересует:',

            reply_markup=blog_btn

        )

        messages_to_delete.append(india_get_back)



    elif message == "⬅️ Наш Блог 📚":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:

                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()

        # Отправляем сообщение о возврате к информации с соответствующей клавиатурой

        back_to_india = await update.message.reply_text('Вы вернулись в Товары из Индии 👳‍♀️', reply_markup=None)
        messages_to_delete.append(back_to_india)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        blog_get_back = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=blog_btn
        )
        messages_to_delete.append(blog_get_back)  # Добавляем в список для удаления

    elif message == "⬅️ Как мы работаем 🛠":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        we_work_res_message = await update.message.reply_text('Вы вернулись в Как мы работаем 🛠', reply_markup=None)
        messages_to_delete.append(we_work_res_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_work = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=how_we_work_btn
        )
        messages_to_delete.append(get_back_work)  # Добавляем в список для удаления

    elif message == "Способы оплаты 🏧":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        reply_res_message = await update.message.reply_text('💰 Оплата индийских товаров и услуг доступна только по безналичному расчету.\n\n'
                                        '📧 Мы выставим счет по электронной почте.\n👇 🏧 Способы оплаты', reply_markup=None)
        messages_to_delete.append(reply_res_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        pay_get_back = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=goa_pay_btn
        )
        messages_to_delete.append(pay_get_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_reply = await update.message.reply_text(
            '♻️💳 Варианты электронных платежных систем',
            reply_markup=reply_markup_pay
        )
        messages_to_delete.append(get_back_reply)  # Добавляем в список для удаления

    elif message == "Расчет заказа 💰":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        await update.message.reply_text('📊 Расчет заказа индийских товаров.', reply_markup=None)

        # Отправляем только клавиатуру с минимальным текстом
        pay_get_back = await update.message.reply_text(
            '📧 Мы выставим счет по электронной почте.',
            reply_markup=goa_pay_btn
        )
        messages_to_delete.append(pay_get_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_calculator_pay = await update.message.reply_text(
            '📢 Информация о расчете заказа',
            reply_markup=order_calculation_pay
        )
        messages_to_delete.append(get_back_calculator_pay)  # Добавляем в список для удаления

    elif message == '💸 Курс валют':
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        currency_rates = await get_currency_rates(update, context)
        messages_to_delete.append(currency_rates)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_currency_rates = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=how_we_work_btn
        )
        messages_to_delete.append(get_back_currency_rates)  # Добавляем в список для удаления

    elif message == '📊 Экономика':
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        economic_get_back = await update.message.reply_text('Вы выбрали "📊 Экономика".', reply_markup=None)
        messages_to_delete.append(economic_get_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_economic = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=how_economic_btn
        )
        messages_to_delete.append(get_back_economic)  # Добавляем в список для удаления

    elif message == "🚚 Доставка":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        delivery_back = await update.message.reply_text('Вы выбрали "🚚 Доставка".', reply_markup=None)
        messages_to_delete.append(delivery_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_delivery = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=delivery_btn
        )
        messages_to_delete.append(get_back_delivery)  # Добавляем в список для удаления

    elif message == "📝 Информация о Доставке":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        info_delivery_back = await update.message.reply_text(delivery_info, parse_mode='MarkdownV2', reply_markup=None)
        messages_to_delete.append(info_delivery_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_inf_delivery = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=delivery_btn
        )
        messages_to_delete.append(get_back_inf_delivery)  # Добавляем в список для удаления

    elif message == "🏗 Как работает Склад":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        info_warehouse_back = await update.message.reply_text(warehouse_info, parse_mode='MarkdownV2', reply_markup=None)
        messages_to_delete.append(info_warehouse_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_inf_warehouse = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=warehouse_btn
        )
        messages_to_delete.append(get_back_inf_warehouse)  # Добавляем в список для удаления

    elif message == "🚨 Помощь":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        helps_back_message = await update.message.reply_text('Вы выбрали "🚨 Помощь".', reply_markup=None)
        messages_to_delete.append(helps_back_message)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_helps = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=helps_btn
        )
        messages_to_delete.append(get_back_helps)  # Добавляем в список для удаления

    elif message == "👳‍♂️ Написать обращение":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        helps_back = await update.message.reply_text(manager_info, parse_mode='MarkdownV2', reply_markup=manger_button)
        messages_to_delete.append(helps_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_help = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=helps_btn
        )
        messages_to_delete.append(get_back_help)  # Добавляем в список для удаления

    elif message == "🛒 Мои Покупки":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        my_pay = await update.message.reply_text('Вы перешли в 🛒 Мои Покупки', reply_markup=None)
        messages_to_delete.append(my_pay)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_my_pay = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=pays_btn
        )
        messages_to_delete.append(get_back_my_pay)  # Добавляем в список для удаления

    if message == "🛒":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
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
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        questions_back = await update.message.reply_text('⁉️ Вопрос-Ответ.\n\n'
                                       '👇 Сделайте выбор что вас интересует.', reply_markup=None)
        messages_to_delete.append(questions_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_question = await update.message.reply_text(
            '🗣️❓❗',
            reply_markup=qw_answ_btn_main
        )
        messages_to_delete.append(get_back_question)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_work = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=how_we_work_btn
        )
        messages_to_delete.append(get_back_work)  # Добавляем в список для удаления

        # Добавляем кнопку для публичной оферты
    elif message == "Публичная оферта 📜":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        oferta_back = await update.message.reply_text("📎 👇 Нажмите на кнопку ниже для перехода:", reply_markup=None)
        messages_to_delete.append(oferta_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_oferta = await update.message.reply_text(
            '📖📂',
            reply_markup=offerta_button
        )
        messages_to_delete.append(get_back_oferta)  # Добавляем в список для удаления
        # Отправляем только клавиатуру с минимальным текстом
        get_back_about = await update.message.reply_text(
            '🙌 Выберите ещё что вас интересует:',
            reply_markup=about_btn
        )
        messages_to_delete.append(get_back_about)  # Добавляем в список для удаления

    elif message == "👀 Отследить заказ":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()

        # Отправляем только клавиатуру с минимальным текстом
        get_back_prod = await update.message.reply_text(
            '🏃💨',
            reply_markup=delivery_btn
        )
        messages_to_delete.append(get_back_prod)  # Добавляем в список для удаления
        track_back = await update.message.reply_text("📎 👇 Нажмите на кнопку ниже для перехода:",
                                                     reply_markup=track_button)
        messages_to_delete.append(track_back)  # Добавляем в список для удаления

    elif message == "🎁 Подарки":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        candies_back = await update.message.reply_text("Вы выбрали 🎁 Подарки", reply_markup=products_btn_india)
        messages_to_delete.append(candies_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_candies = await update.message.reply_text(
            '🛍️🎁💖💝',
            reply_markup=gifts_btn_main
        )
        messages_to_delete.append(get_back_candies)  # Добавляем в список для удаления

    elif message in ["👤", "Личный кабинет 👤"]:
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        cabinet_two_back = await update.message.reply_text('Вы вернулись в кабинет 👤', reply_markup=profile_btn)
        messages_to_delete.append(cabinet_two_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_cabinet = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=profile_btn
        )
        messages_to_delete.append(get_back_cabinet)  # Добавляем в список для удаления

    elif message == "🔙 Назад в кабинет":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        cabinet_back = await update.message.reply_text('Вы вернулись в кабинет 👤', reply_markup=None)
        messages_to_delete.append(cabinet_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_cabinet = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=profile_btn
        )
        messages_to_delete.append(get_back_cabinet)  # Добавляем в список для удаления

    elif message == "📁 Каталог":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        clear_catalog_text = await update.message.reply_text('🪶🦚राधे राधे𓃔🦚\n\n📍 Вы выбрали - Каталог 📁  Goabay.com \n〰️〰️〰️', reply_markup=None)
        messages_to_delete.append(clear_catalog_text)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        india_del_catalog = await update.message.reply_text(
            '🛍️ Выбирите категорию товара 👇',
            reply_markup=catalog_btn,
        )
        messages_to_delete.append(india_del_catalog)
        india_inline_catalog = await update.message.reply_text(
            '🛒🛍️👠✨ Категории товаров:',
            reply_markup=create_category_keyboard()
        )
        messages_to_delete.append(india_inline_catalog)  # Добавляем в список для удаления

    elif message == "🏪 Магазин":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        clear_store_text = await update.message.reply_text('Вы выбрали 🏪 Магазин goabay.com', reply_markup=None)
        messages_to_delete.append(clear_store_text)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        india_del_store = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=catalog_btn
        )
        messages_to_delete.append(india_del_store)  # Добавляем в список для удаления
        # Запрос ссылки на товар
    if message == "🔗 Ввести ссылку Goabay":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        link_back = await update.message.reply_text("🔗 Введите ссылку https:// 👇 на Товар 🛍️ магазина 🏝GoaBay.com ", reply_markup=None)
        messages_to_delete.append(link_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_link = await update.message.reply_text(
            'જ⁀➴',
            reply_markup=catalog_btn
        )
        messages_to_delete.append(get_back_link)  # Добавляем в список для удаления

    elif message == "🛍 Товары на складе":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        info_category_warehouse_back = await update.message.reply_text(
            '🪶🦚राधे राधे𓃔🦚\n\n📍 Вы выбрали 🛍 Товары на складе \n🗃 Выбирите категорию товара 👇\n〰️〰️〰️',
            reply_markup=create_category_keyboard())
        messages_to_delete.append(info_category_warehouse_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_back_category_warehouse = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=warehouse_btn
        )
        messages_to_delete.append(get_back_category_warehouse)  # Добавляем в список для удаления

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

    elif message == "✈️ Авиабилеты":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        info_avia_back = await update.message.reply_text(avia_answer_txt, parse_mode='MarkdownV2', reply_markup=None)
        messages_to_delete.append(info_avia_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_avia_inf = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=profile_avia_btn
        )
        messages_to_delete.append(get_avia_inf)  # Добавляем в список для удаления


    elif message == "🏘 Гоа Аренда":
        # Удаляем все сообщения из списка, если они были отправлены ранее
        for msg in messages_to_delete:
            try:
                await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)

            except Exception as e:

                logging.error(f"Ошибка при удалении сообщения: {e}")

        # Очищаем список после удаления

        messages_to_delete.clear()
        info_avia_back = await update.message.reply_text(hotel_answer_txt, parse_mode='MarkdownV2', reply_markup=None)
        messages_to_delete.append(info_avia_back)  # Добавляем в список для удаления

        # Отправляем только клавиатуру с минимальным текстом
        get_hotel_inf = await update.message.reply_text(
            '🙌 Выберите что вас интересует:',
            reply_markup=profile_hotel_btn
        )
        messages_to_delete.append(get_hotel_inf)  # Добавляем в список для удаления


    # elif message == "✈️ Забронировать Билеты":
    #     # Удаляем все сообщения из списка, если они были отправлены ранее
    #     for msg in messages_to_delete:
    #         try:
    #             await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)
    #
    #         except Exception as e:
    #
    #             logging.error(f"Ошибка при удалении сообщения: {e}")
    #
    #     # Очищаем список после удаления
    #
    #     messages_to_delete.clear()
    #     info_avia_back = await update.message.reply_text(avia_answer_txt, parse_mode='MarkdownV2', reply_markup=None)
    #     messages_to_delete.append(info_avia_back)  # Добавляем в список для удаления
    #
    #     # Отправляем только клавиатуру с минимальным текстом
    #     get_avia_inf = await update.message.reply_text(
    #         '🙌 Выберите что вас интересует:',
    #         reply_markup=profile_avia_btn
    #     )
    #     messages_to_delete.append(get_avia_inf)  # Добавляем в список для удаления
