import datetime
from pycbrf import ExchangeRates
from telegram import Update
from telegram.ext import CallbackContext
from prettytable import PrettyTable


async def get_currency_rates(update: Update, context: CallbackContext) -> None:
    rates = ExchangeRates(datetime.datetime.now())

    # Получаем актуальные курсы валют
    inr_to_rub = rates['INR'].value / 100  # Курс индийской рупии к рублю (за 100 INR)
    usd_to_rub = rates['USD'].value  # Курс доллара к рублю
    eur_to_rub = rates['EUR'].value  # Курс евро к рублю
    cny_to_rub = rates['CNY'].value

    # Создаем таблицу с помощью PrettyTable
    table = PrettyTable()
    table.field_names = ["💰 Валюта", "Курс к 🇷🇺 RUB"]

    # Устанавливаем выравнивание столбцов
    table.align["💰 Валюта"] = "l"  # Выравнивание по левому краю
    table.align["Курс к 🇷🇺 RUB"] = "r"  # Выравнивание по правому краю

    # Устанавливаем максимальную ширину для столбцов
    table.max_width["💰 Валюта"] = 24  # Максимальная ширина для валюты
    table.max_width["Курс к 🇷🇺 RUB"] = 14  # Максимальная ширина для курса

    # Добавляем данные в таблицу с форматированием
    table.add_row([f"{'🇮🇳 Индийская рупия':<24}", f"{inr_to_rub:.2f}"])
    table.add_row(["-" * 24, "-" * 14])  # Горизонтальная линия между строками
    table.add_row([f"{'🇺🇸 Доллар':<24}", f"{usd_to_rub:.2f}"])
    table.add_row(["-" * 24, "-" * 14])  # Горизонтальная линия между строками
    table.add_row([f"{'🇪🇺 Евро':<24}", f"{eur_to_rub:.2f}"])
    table.add_row(["-" * 24, "-" * 14])  # Горизонтальная линия между строками
    table.add_row([f"{'🇨🇳 Юань':<24}", f"{cny_to_rub:.2f}"])

    # Получаем строковое представление таблицы
    response = '```\n{}```'.format(table.get_string())

    await update.message.reply_text(response, parse_mode='Markdown')
