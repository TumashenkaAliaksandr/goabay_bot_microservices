# Получение курсов валют
import datetime

from pycbrf import ExchangeRates
from telegram import Update
from telegram.ext import CallbackContext


async def get_currency_rates(update: Update, context: CallbackContext) -> None:
    rates = ExchangeRates(datetime.datetime.now())

    message = (
        "Курсы валют:\n"
        f"1 INR = {1 / rates['INR'].value:.4f} RUB\n"
        f"1 USD = {1 / rates['USD'].value:.4f} RUB\n"
        f"1 EUR = {1 / rates['EUR'].value:.4f} RUB"
    )

    await update.message.reply_text(message)
