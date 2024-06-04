import telebot
from django.http import HttpResponse

from goabay_bot import settings

bot = telebot.TeleBot(settings.BOT_TOKEN)


def index(request):
    if request.method == "POST":
        update = telebot.types.Update.de_json(request.body.decode('utf-8'))
        bot.process_new_updates([update])

    return HttpResponse('<h1>Ты подключился!</h1>')
