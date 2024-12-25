import telebot
from django.http import HttpResponse
from django.shortcuts import render

from bot_app.models import Product
from goabay_bot import settings

bot = telebot.TeleBot(settings.BOT_TOKEN)


# def index(request):
#     if request.method == "POST":
#         update = telebot.types.Update.de_json(request.body.decode('utf-8'))
#         bot.process_new_updates([update])
#
#     products_up_block = Product.objects.all()
#
#     context = {
#         'products_up_block': products_up_block,
#     }
#     return render(request, 'webapp/index.html', context=context)
