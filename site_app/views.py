import telebot
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from bot_app.models import Product
from goabay_bot import settings
from site_app.forms import NewsletterForm
from site_app.models import NewsletterSubscription, SliderImage

from .forms import NewsletterForm

# bot = telebot.TeleBot(settings.BOT_TOKEN)



def index(request):

    products_up_block = Product.objects.all()[:8]
    sliders = SliderImage.objects.all()
    context = {
        'products_up_block': products_up_block,
        'sliders': sliders,
    }
    return render(request, 'webapp/index.html', context=context)


def category_view(request, category_name):
    # Логика для отображения категории
    return render(request, 'webapp/shop/category.html', {'category': category_name})



def product_detail(request, name, slug):
    products = get_object_or_404(Product, name=name)  # Получаем продукт по name
    product = get_object_or_404(Product, slug=slug)
    product_name = Product.objects.all()
    context = {
        'products': products,
        'product': product,
        'product_name': product_name,
    }
    return render(request, 'webapp/shop/product_detail.html', context)

def wishlist(request):
    return render(request, 'webapp/wishlist.html')

def compare(request):
    return render(request, 'webapp/shop/compare.html')

def product(request):
    return render(request, 'webapp/shop/product.html')

def shop(request):
    return render(request, 'webapp/shop/shop.html')

def checkout(request):
    return render(request, 'webapp/shop/checkout.html')

def cart(request):
    return render(request, 'webapp/shop/cart.html')

def about(request):
    return render(request, 'webapp/about.html')


def news(request):
    return render(request, 'webapp/blog/blog.html')


def contact(request):
    return render(request, 'webapp/contact.html')


def account(request):
    return render(request, 'webapp/account/account.html')


def login(request):
    return render(request, 'webapp/account/login.html')


def registrations(request):
    return render(request, 'webapp/account/register.html')


def forgot_password(request):
    return render(request, 'webapp/account/forgot-password.html')


def four_zero_four(request):
    return render(request, 'webapp/404.html')


# def newsletter_signup(request):
#     if request.method == 'POST':
#         form = NewsletterForm(request.POST)
#
#         # Проверяем, валидна ли форма
#         if form.is_valid():
#             # Сохраняем подписку
#             form.save()
#
#             # Ответ на успешную подписку
#             return JsonResponse({'status': 'success'})
#         else:
#             # Ошибка, если форма не валидна
#             return JsonResponse({'status': 'error', 'message': 'Invalid email or missing data.'})
#
#     return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
#


def newsletter_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        permission = request.POST.get('permission') == 'on'  # Преобразуем значение чекбокса в булево значение

        if email:
            # Сохраняем подписку в базе данных
            subscription = NewsletterSubscription.objects.create(email=email, permission=permission)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Email is required.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def get_slider_images(request):
    images = SliderImage.objects.all().order_by('-created_at')
    image_list = [{'url': image.image.url} for image in images]
    return JsonResponse({'images': image_list})


# def slider_view(request):
#     slides = SliderImage.objects.all()
#     return render(request, 'webapp/index.html', {'slides': slides})

def product_catalog(request):
    return render(request, 'webapp/shop/product-catalog.html')


def how_we_work(request):
    return render(request, 'webapp/how-we-work.html')


def brand(request):
    return render(request, 'webapp/shop/brand.html')

def single_brand(request, name, slug):
    return render(request, 'webapp/shop/single_brand.html')

def elephant(request):
    products_up_block = Product.objects.all()[:8]
    sliders = SliderImage.objects.all()
    context = {
        'products_up_block': products_up_block,
        'sliders': sliders,
    }
    return render(request, 'webapp/blog/elephant.html', context=context)
