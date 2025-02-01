import telebot
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from bot_app.models import Product
from goabay_bot import settings

# bot = telebot.TeleBot(settings.BOT_TOKEN)



def index(request):

    products_up_block = Product.objects.all()

    context = {
        'products_up_block': products_up_block,
    }
    return render(request, 'webapp/index.html', context=context)


def product_detail(request, id, slug):
    products = get_object_or_404(Product, id=id)  # Получаем продукт по ID
    product = get_object_or_404(Product, slug=slug)
    product_name = Product.objects.all()
    context = {
        'products': products,
        'product': product,
        'product_name': product_name,
    }
    return render(request, 'webapp/product_detail.html', context)


def news(request):
    return render(request, 'webapp/blog/blog.html')
