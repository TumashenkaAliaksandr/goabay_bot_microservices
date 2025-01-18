from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, ConversationHandler
import requests
import logging

from bot_app.templates.webapp.answers.info_back import messages_to_delete
from bot_app.templates.webapp.buttons.buttons_store import profile_avia_btn
from bot_app.templates.webapp.text_files_py_txt import register_avia_handler

API_KEY = "ваш_ключ_авиасейлс"  # Ваш API-ключ Aviasales
BASE_URL = "https://api.travelpayouts.com/v1/prices/cheap"  # API-адрес

# Логгирование
logging.basicConfig(level=logging.INFO)

# Этапы для ConversationHandler
ORIGIN, DESTINATION, DEPART_DATE, RETURN_DATE, PASSENGERS, CHILDREN_ASK, CHILDREN_INFO, CHILDREN_AGE, FLIGHT_CLASS = range(9)

# Функция для получения билетов
def get_cheap_tickets(origin, destination, depart_date, return_date, passengers, flight_class, children_info=None, currency="rub"):
    params = {
        "origin": origin,
        "destination": destination,
        "depart_date": depart_date,
        "return_date": return_date,
        "currency": currency,
        "token": API_KEY,
        "passengers": passengers,
        "flight_class": flight_class,
    }
    # Добавляем информацию о детях
    if children_info:
        params["children"] = children_info

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"ⓘ Ошибка API: {e}"

    data = response.json()
    if data.get("success"):
        tickets = data.get("data", {}).get(destination, {})
        result = [
            f"🛫 Рейс: {flight}\n💲 Цена: {details['price']} {currency}\nСсылка: {details.get('link', 'Нет ссылки')}"
            for flight, details in tickets.items()
        ]
        return "\n\n".join(result) if result else "🎫 Билеты не найдены."
    else:
        return f"Ошибка: {data.get('error', 'ⓘ Неизвестная ошибка')}"

# Начало процесса
async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(register_avia_handler.city_fly_up, parse_mode='MarkdownV2', reply_markup=ReplyKeyboardRemove())
    return ORIGIN

# Получаем город вылета
async def get_origin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["origin"] = update.message.text.strip().upper()
    await update.message.reply_text(register_avia_handler.city_fly_down, parse_mode='MarkdownV2')
    return DESTINATION

# Получаем город прилета
async def get_destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["destination"] = update.message.text.strip().upper()
    await update.message.reply_text(register_avia_handler.date_fly_up, parse_mode='MarkdownV2')
    return DEPART_DATE

# Получаем дату вылета
async def get_depart_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["depart_date"] = update.message.text.strip()
    await update.message.reply_text(register_avia_handler.date_fly_down, parse_mode='MarkdownV2')
    return RETURN_DATE

# Получаем дату обратного рейса
async def get_return_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return_date = None if update.message.text.lower() == "нет" else update.message.text.strip()
    context.user_data["return_date"] = return_date
    await update.message.reply_text(register_avia_handler.quantity_peoples_for_fly, parse_mode='MarkdownV2')
    return PASSENGERS

# Получаем количество пассажиров
async def get_passengers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    passengers = update.message.text.strip()
    if not passengers.isdigit() or int(passengers) <= 0:
        await update.message.reply_text(register_avia_handler.correct_quantity_peoples_for_fly, parse_mode='MarkdownV2')
        return PASSENGERS
    context.user_data["passengers"] = passengers
    await update.message.reply_text("Есть ли дети?", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Да", callback_data='children_yes'), InlineKeyboardButton("Нет", callback_data='children_no')]
    ]))
    return CHILDREN_ASK

# Обработка кнопок с ответами (Да/Нет)
async def handle_children_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "children_yes":
        await query.edit_message_text(register_avia_handler.children_yes_answer, parse_mode='MarkdownV2')
        return CHILDREN_INFO
    elif query.data == "children_no":
        # Пропускаем шаг с детьми и переходим к следующему
        context.user_data["children_info"] = None
        await query.edit_message_text(register_avia_handler.class_business_eco, parse_mode='MarkdownV2')
        return FLIGHT_CLASS

# Обрабатываем информацию о детях
async def process_children_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    children_info = update.message.text.strip()
    try:
        # Пример ввода: "2: 5, 8"
        children_list = [int(age.strip()) for age in children_info.split(":")[1].split(",")]
        context.user_data["children_info"] = children_list
        await update.message.reply_text(register_avia_handler.class_business_eco, parse_mode='MarkdownV2')
        return FLIGHT_CLASS
    except Exception:
        await update.message.reply_text(register_avia_handler.children_age, parse_mode='MarkdownV2')
        return CHILDREN_INFO

# Получаем возраст детей
async def get_children_ages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    children_ages = update.message.text.strip()
    try:
        # Пример ввода: '5, 8' для детей 5 и 8 лет
        children_ages_list = [int(age.strip()) for age in children_ages.split(",")]
        context.user_data["children_ages"] = children_ages_list
        await update.message.reply_text(register_avia_handler.class_business_eco, parse_mode='MarkdownV2')
        return FLIGHT_CLASS
    except Exception:
        await update.message.reply_text(register_avia_handler.children_age_please, parse_mode='MarkdownV2')
        return CHILDREN_AGE

# Получаем класс перелета и завершаем процесс
async def get_flight_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if "эконом" in text:
        flight_class = "economy"
    elif "бизнес" in text:
        flight_class = "business"
    else:
        await update.message.reply_text(register_avia_handler.class_business_eco, parse_mode='MarkdownV2')
        return FLIGHT_CLASS

    context.user_data["flight_class"] = flight_class

    # Поиск билетов
    data = context.user_data
    tickets = get_cheap_tickets(
        origin=data["origin"],
        destination=data["destination"],
        depart_date=data["depart_date"],
        return_date=data["return_date"],
        passengers=data["passengers"],
        flight_class=data["flight_class"],
        children_info=data.get("children_info"),
    )

    # Формирование ссылки для бронирования
    aviasales_url = f"https://www.aviasales.ru/search/{data['origin']}{data['destination']}{data['depart_date'].replace('-', '')}"
    keyboard = [[InlineKeyboardButton("Забронировать 👌", url=aviasales_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    get_avia_inf_tickets = await update.message.reply_text('🙌 Выберите что вас интересует:',
                                                           reply_markup=profile_avia_btn)
    messages_to_delete.append(get_avia_inf_tickets)

    await update.message.reply_text(f"♻️ Результаты поиска:\n\n{tickets}", reply_markup=reply_markup)
    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ⓘ Процесс бронирования отменен. ⛔", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END