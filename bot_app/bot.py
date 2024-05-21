import logging
import pika
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
# from telegram.ext import Filters
from django.conf import settings

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def send_to_rabbitmq(message: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE)
    channel.basic_publish(exchange='', routing_key=settings.RABBITMQ_QUEUE, body=message)
    connection.close()

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я ваш телеграм-бот.')

def echo(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    send_to_rabbitmq(message)
    update.message.reply_text('Ваше сообщение отправлено в очередь RabbitMQ.')

def main() -> None:
    updater = Updater(settings.BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
