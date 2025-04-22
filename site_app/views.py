import telebot
from celery import shared_task
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Prefetch
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from site_app.models import Product, Brand, NewsletterSubscription, Category
from main_parcer.scripts_parcers.isha_bestsellers import scrape_bestsellers


# bot = telebot.TeleBot(settings.BOT_TOKEN)



def index(request):
    products_up_block = Product.objects.all()
    sliders = Brand.objects.all()
    context = {
        'products_up_block': products_up_block,
        'sliders': sliders,
    }
    return render(request, 'main/nick/index.html', context=context)


def category_view(request, category_name):
    # Логика для отображения категории
    return render(request, 'webapp/shop/category.html', {'category': category_name})



def product_detail(request, name, slug):
    products = get_object_or_404(Product, name=name)  # Получаем продукт по name
    product = get_object_or_404(Product, slug=slug)
    product_name = Product.objects.all()
    products_up_block = Product.objects.all()
    context = {
        'products': products,
        'product': product,
        'product_name': product_name,
        'products_up_block': products_up_block,

    }
    return render(request, 'main/nick/single-product.html', context)

def compare(request):
    return render(request, 'webapp/shop/compare.html')

def product(request):
    return render(request, 'webapp/shop/product.html')

def shop(request):
    return render(request, 'webapp/shop/shop.html')

def checkout(request):
    return render(request, 'webapp/shop/checkout.html')

def news(request):
    return render(request, 'webapp/blog/blog.html')


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


def products_brands(request, slug=None):
    # Основной QuerySet с аннотацией бренда
    products_qs = Product.objects.select_related('brand').prefetch_related(
        Prefetch('category', queryset=Category.objects.only('name'))
    ).order_by('-id')

    # Фильтрация и аннотация бренда
    if slug:
        products_qs = products_qs.filter(brand__slug=slug)
        brand_obj = Brand.objects.filter(slug=slug).first()
    else:
        brand_obj = None

    # Оптимизированная пагинация
    paginator = Paginator(products_qs, 15)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    # AJAX-запрос
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string(
            'main/nick/products_partial.html',
            {'products_up_block': page_obj}
        )

        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages
        })

    # Контекст для полной загрузки
    context = {
        'products_up_block': page_obj,
        'brand': brand_obj,
        'sliders': Brand.objects.all(),
        'categories': Category.objects.all(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages
    }

    return render(request, 'main/nick/products_brands.html', context)


def archive(request):
    return render(request, 'main/nick/product-archive.html')


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
    images = Brand.objects.all().order_by('-created_at')
    image_list = [{'url': image.image.url} for image in images]
    return JsonResponse({'images': image_list})


# def slider_view(request):
#     slides = SliderImage.objects.all()
#     return render(request, 'images/test-index.html', {'slides': slides})

def product_catalog(request):
    products_up_block = Product.objects.all()
    sliders = Brand.objects.all()
    context = {
        'products_up_block': products_up_block,
        'sliders': sliders,
    }
    return render(request, 'webapp/shop/product-catalog.html', context=context)



def brand(request):
    products_up_block = Product.objects.all()
    sliders = Brand.objects.all()
    context = {
        'products_up_block': products_up_block,
        'sliders': sliders,
    }
    return render(request, 'main/nick/products_brands.html', context=context)


# def brand_name(request, slug):
#     brand_obj = Brand.objects.filter(slug=slug).first()
#     if brand_obj:
#         products_up_block = Product.objects.filter(brand=brand_obj)
#         sliders = Brand.objects.all()
#         context = {
#             'products_up_block': products_up_block,
#             'sliders': sliders,
#         }
#         return render(request, 'main/nick/products_brands.html', context=context)
#     else:
#         return HttpResponseNotFound("Бренд не найден")


def single_brand(request, name, slug):
    products = get_object_or_404(Product, name=name)  # Получаем продукт по name
    product = get_object_or_404(Product, slug=slug)
    product_name = Product.objects.all()
    products_up_block = Product.objects.all()
    context = {
        'products': products,
        'product': product,
        'product_name': product_name,
        'products_up_block': products_up_block,

    }
    return render(request, 'webapp/shop/single_brand.html', context=context)


def elephant(request):
    products_up_block = Product.objects.all()[:8]
    sliders = Brand.objects.all()
    context = {
        'products_up_block': products_up_block,
        'sliders': sliders,
    }
    return render(request, 'webapp/blog/elephant.html', context=context)


def bestsellers(request):
    return render(request, 'webapp/shop/bestsellers.html')


def handmade(request):
    return render(request, 'webapp/shop/bestsellers.html')

# def serve_json(request):
#     try:
#         with open('D:\\my_projects\\goabay_bot\\main_parcer\\scripts_parcers\\jsons\\isha_bestsellers_products.json', 'r') as f: # надо будет на забыть поменять путь
#             data = json.load(f)
#         return JsonResponse(data, safe=False)
#     except FileNotFoundError:
#         return JsonResponse({"error": "Файл не найден"}, status=404)
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Ошибка парсинга JSON"}, status=500)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)



@shared_task
def update_ishalife_products():
    url = 'https://ishalife.sadhguru.org/'
    products = scrape_bestsellers(url)

    # Очистка кеша после обновления
    cache.delete('ishalife_products')  # Удаляем старые данные из кеша
    cache.set('ishalife_products', products, timeout=86400)  # Добавляем новые данные в кеш



@require_http_methods(['POST'])
def add_to_cart(request):
    try:
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        product = get_object_or_404(Product, id=product_id)

        # Логика добавления в корзину (пример с использованием сессии)
        cart = request.session.get('cart', {})
        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity
        request.session['cart'] = cart

        # Возвращаем общее количество товаров в корзине
        total_quantity = sum(cart.values())
        return JsonResponse({'success': True, 'message': 'Товар добавлен в корзину', 'total_quantity': total_quantity})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            # Обработка ситуации, когда товар не найден
            pass

    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'main/nick/cart.html', context)

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
    return redirect('cart')
