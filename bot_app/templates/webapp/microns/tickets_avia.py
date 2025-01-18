from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters, ConversationHandler
import requests
import logging

API_KEY = "ваш_ключ_авиасейлс"  # Ваш API-ключ Aviasales
BASE_URL = "https://api.travelpayouts.com/v1/prices/cheap"  # API-адрес

# Логгирование
logging.basicConfig(level=logging.INFO)

# Этапы для ConversationHandler
ORIGIN, DESTINATION, DEPART_DATE, RETURN_DATE, PASSENGERS, FLIGHT_CLASS = range(6)

# Функция для получения билетов
def get_cheap_tickets(origin, destination, depart_date, return_date, passengers, flight_class, currency="rub"):
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
    await update.message.reply_text(
        "🏙 🛫  Введите город вылета:",
        reply_markup=ReplyKeyboardRemove()
    )
    return ORIGIN

# Получаем город вылета
async def get_origin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["origin"] = update.message.text.strip().upper()
    await update.message.reply_text("🏙 🪂  Введите город прилета:")
    return DESTINATION

# Получаем город прилета
async def get_destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["destination"] = update.message.text.strip().upper()
    await update.message.reply_text("📅 🗺️⁀જ✈ Введите дату вылета (ГГГГ-ММ-ДД):")
    return DEPART_DATE

# Получаем дату вылета
async def get_depart_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["depart_date"] = update.message.text.strip()
    await update.message.reply_text("📅 🗺️⁀જ✈ Введите дату обратного рейса (или напишите 'нет'):")
    return RETURN_DATE

# Получаем дату обратного рейса
async def get_return_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return_date = None if update.message.text.lower() == "нет" else update.message.text.strip()
    context.user_data["return_date"] = return_date
    await update.message.reply_text("👥 Введите количество пассажиров:")
    return PASSENGERS

# Получаем количество пассажиров
async def get_passengers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    passengers = update.message.text.strip()
    if not passengers.isdigit() or int(passengers) <= 0:
        await update.message.reply_text("👥 Введите корректное количество пассажиров.")
        return PASSENGERS
    context.user_data["passengers"] = passengers
    await update.message.reply_text("🔰 Напишите класс:\n🪑 Эконом или 💺 Бизнес:")
    return FLIGHT_CLASS

# Получаем класс перелета и завершаем процесс
async def get_flight_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if "эконом" in text:
        flight_class = "economy"
    elif "бизнес" in text:
        flight_class = "business"
    else:
        await update.message.reply_text("🔰 Пожалуйста, напишите:\n🪑 'Эконом' или 💺 'Бизнес'.")
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
    )

    # Формирование ссылки для бронирования
    aviasales_url = f"https://www.aviasales.ru/search/{data['origin']}{data['destination']}{data['depart_date'].replace('-', '')}"
    keyboard = [[InlineKeyboardButton("Забронировать 👌", url=aviasales_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"♻️ Результаты поиска:\n\n{tickets}", reply_markup=reply_markup)

    # Завершаем процесс
    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ⓘ Процесс бронирования отменен. ⛔", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
