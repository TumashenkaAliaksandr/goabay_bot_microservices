import ast
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import AccountDetailsForm, UserProfileForm
from celery import shared_task
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Prefetch
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from rest_framework import generics
from django.contrib.auth import authenticate, login as login_reg
from bot_app.models import Review, ProductVariant, UserRegistration, UserProfile
from goabay_bot import settings
from site_app.forms import ReviewForm, RegistrationForm
from site_app.models import Product, Brand, NewsletterSubscription, Category, VerticalMenuName, VerticalMenu
from main_parcer.scripts_parcers.isha_bestsellers import scrape_bestsellers
from site_app.serializers import ProductSerializer
from site_app.templatetags.utils import get_rating_breakdown




def index(request):
    products_up_block = Product.objects.all()
    sliders = Brand.objects.all()
    menu_name_obj = VerticalMenuName.objects.first()
    menu_name = menu_name_obj.name if menu_name_obj else "Menu"
    menu_items = VerticalMenu.objects.all()
    context = {
        'products_up_block': products_up_block,
        'sliders': sliders,
        'menu_name': menu_name,
        'menu_items': menu_items,
    }
    return render(request, 'webapp/index.html', context=context)


# def account(request):
#     """Account page"""
#     return render(request, 'main/nick/account.html')


def category_view(request, category_name):
    # Логика для отображения категории
    return render(request, 'webapp/shop/category.html', {'category': category_name})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product_name = Product.objects.all()
    products_up_block = Product.objects.all()
    reviews = Review.objects.filter(product_slug=slug).order_by('-created_at')

    has_variants = product.variants.exists()

    variant_sizes = []
    variant_colors = []
    variants_with_images = []
    first_variant = None
    variant_additional_images = []

    if has_variants:
        # Получаем уникальные размеры из вариаций
        variant_sizes_raw = product.variants.values_list('size', flat=True).distinct()
        for size_str in variant_sizes_raw:
            if not size_str:
                continue
            try:
                parsed = ast.literal_eval(size_str)
                if isinstance(parsed, list):
                    variant_sizes.extend(parsed)
                else:
                    variant_sizes.append(size_str)
            except (ValueError, SyntaxError):
                variant_sizes.append(size_str)
        variant_sizes = sorted(set(filter(None, variant_sizes)))

        # Получаем уникальные цвета из вариаций
        variant_colors_raw = product.variants.values_list('color', flat=True).distinct()
        variant_colors = sorted(set(filter(None, variant_colors_raw)))

        # Получаем список вариаций с цветом и изображением для шаблона
        variant_data = product.variants.values('color', 'image').distinct()
        for var in variant_data:
            img_path = var['image']
            img_url = f"{settings.MEDIA_URL.rstrip('/')}/{img_path.lstrip('/')}" if img_path else None
            variants_with_images.append({
                'color': var['color'],
                'image_url': img_url,
            })

        # Определяем выбранный цвет из GET параметра, если есть
        selected_color = request.GET.get('color')
        if selected_color and selected_color in variant_colors:
            first_variant = product.variants.filter(color=selected_color).first()
        else:
            first_variant = product.variants.first()

        # Получаем дополнительные изображения выбранной вариации
        if first_variant:
            if first_variant.image:
                main_img_url = f"{settings.MEDIA_URL.rstrip('/')}/{first_variant.image.name.lstrip('/')}"
                variant_additional_images.append({'image_url': main_img_url})
            for img in first_variant.additional_images.all():
                img_url = f"{settings.MEDIA_URL.rstrip('/')}/{img.image.name.lstrip('/')}"
                if not any(i['image_url'] == img_url for i in variant_additional_images):
                    variant_additional_images.append({'image_url': img_url})

        # Если вариаций мало (0 или 1), добавляем все доп фото продукта в миниатюры
        if product.variants.count() <= 1:
            for img in product.additional_images.all():
                img_url = f"{settings.MEDIA_URL.rstrip('/')}/{img.image.name.lstrip('/')}"
                if not any(i['image_url'] == img_url for i in variant_additional_images):
                    variant_additional_images.append({'image_url': img_url})

        # Получаем размеры выбранной вариации для передачи в шаблон
        variant_sizes = []
        if first_variant and first_variant.size:
            try:
                parsed_sizes = ast.literal_eval(first_variant.size)
                if isinstance(parsed_sizes, list):
                    variant_sizes = parsed_sizes
                else:
                    variant_sizes = [first_variant.size]
            except (ValueError, SyntaxError):
                variant_sizes = [first_variant.size]

    else:
        # Для простого товара (нет вариаций)
        if hasattr(product, 'additional_images') and product.image:
            main_img_url = f"{settings.MEDIA_URL.rstrip('/')}/{product.image.name.lstrip('/')}"
            variant_additional_images.append({'image_url': main_img_url})
        for img in product.additional_images.all():
            img_url = f"{settings.MEDIA_URL.rstrip('/')}/{img.image.name.lstrip('/')}"
            if not any(i['image_url'] == img_url for i in variant_additional_images):
                variant_additional_images.append({'image_url': img_url})

    # Обработка формы отзыва
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product_slug = slug
            review.save()
            return redirect('product_detail', slug=slug)
    else:
        form = ReviewForm()

    ratings = [review.rating * 20 for review in reviews]
    rating_breakdown = get_rating_breakdown(ratings)
    total_votes = len(ratings)

    context = {
        'product': product,
        'product_name': product_name,
        'products_up_block': products_up_block,
        'rating_breakdown': rating_breakdown,
        'total_votes': total_votes,
        'form': form,
        'reviews': reviews,
        'variant_sizes': variant_sizes,
        'variant_colors': variant_colors,
        'variants_with_images': variants_with_images,
        'first_variant': first_variant,
        'variant_additional_images': variant_additional_images,
        'has_variants': has_variants,
    }
    return render(request, 'webapp/shop/single-product.html', context)

def get_variant_images(request, product_id, color):
    variant = ProductVariant.objects.filter(product_id=product_id, color=color).first()
    if not variant:
        return JsonResponse({'error': 'Not found'}, status=404)

    images = []
    if variant.image:
        images.append(request.build_absolute_uri(variant.image.url))
    for img in variant.additional_images.all():
        images.append(request.build_absolute_uri(img.image.url))

    # Предположим, что variant.size — строка с размерами, например, "['S', 'M', 'L']"
    try:
        sizes = ast.literal_eval(variant.size) if variant.size else []
    except:
        sizes = [variant.size] if variant.size else []

    return JsonResponse({
        'images': images,
        'sizes': sizes,
    })

def compare(request):
    return render(request, 'webapp/shop/compare.html')

def product(request):
    return render(request, 'webapp/shop/product.html')

def shop(request):
    return render(request, 'webapp/shop/shop.html')


def payments(request):
    return render(request, 'webapp/shop/payment.html')


def checkout(request):
    return render(request, 'webapp/shop/checkout.html')


def orders(request):
    return render(request, 'webapp/account/orders.html')

def news(request):
    return render(request, 'webapp/blog/blog.html')


def login(request):
    brands = Brand.objects.all().order_by('name')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('pass', '')

        # Найдем пользователя по email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is not None:
            # Аутентифицируем по username и паролю
            user_auth = authenticate(request, username=user.username, password=password)
            if user_auth is not None:
                auth_login(request, user_auth)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('account')  # Замените на нужный URL после логина
            else:
                messages.error(request, 'Incorrect password. Please try again.')
        else:
            messages.error(request, 'You are not registered. Please sign up first.')

    context = {
        'brands': brands,
    }

    return render(request, 'webapp/account/login.html', context=context)


def logout(request):
    if request.method == 'POST':
        auth_logout(request)
        messages.info(request, "You have successfully logged out.")
        return redirect('login')  # Или другой URL для перенаправления
    else:
        # Если заходят GET-запросом, например, редиректим на страницу аккаунта или логина
        return redirect('account')  # Или 'login'


def registrations(request):
    brands = Brand.objects.all().order_by('name')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            # попытка автоматически залогинить
            user = authenticate(username=user.username, password=raw_password)
            if user is not None:
                login_reg(request, user)  # Используем django.contrib.auth.login под именем login_reg
                messages.success(request, 'Регистрация прошла успешно. Вы вошли в аккаунт.')
                return redirect('account')  # Замените на ваше имя URL для аккаунта
            else:
                messages.warning(request, 'Регистрация завершена, но автоматический вход не удался. Пожалуйста, войдите вручную.')
                return redirect('login')  # Замените на имя вашей страницы логина, если нужно
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = RegistrationForm()



    return render(request, 'webapp/account/register.html', {'form': form, 'brands': brands})




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


def single_brand(request, slug):
    # Получаем все продукты данного бренда по слагу бренда
    brand_obj = get_object_or_404(Brand, slug=slug)  # Получаем объект бренда по слагу

    # Получаем все продукты, связанные с этим брендом
    products_qs = Product.objects.filter(brand=brand_obj).select_related('brand').prefetch_related(
        Prefetch('category', queryset=Category.objects.only('name'))
    ).order_by('-id')  # Все продукты этого бренда, отсортированные по id

    # Получаем конкретный продукт по слагу
    product = get_object_or_404(Product, slug=slug)

    context = {
        'products': products_qs,  # Все продукты этого бренда
        'product': product,  # Один конкретный продукт
        'brand': brand_obj,  # Информация о бренде
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
#         with open('D:\\my_projects\\goabay_bot\\main_parcer\\scripts_parcers\\jsons_files\\isha_bestsellers_products.json', 'r') as f: # надо будет на забыть поменять путь
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
    return render(request, 'webapp/shop/cart.html', context)

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
    return redirect('cart')


def contacts (request):
    return render(request, 'main/nick/contacts.html')


# APIview for flitter flow - mobile app

class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'  # Чтобы искать по слагу, если нужно


def wishlist(request):
    # тестовая страница или пока пустая
    return render(request, 'webapp/wishlist.html')


@login_required
def account(request):
    user = request.user

    # Получить связанные объекты
    registration, _ = UserRegistration.objects.get_or_create(user_id=user.id, defaults={'name': user.get_full_name() or user.username, 'email': user.email})
    profile, _ = UserProfile.objects.get_or_create(registration=registration)

    if request.method == 'POST':
        user_form = AccountDetailsForm(request.POST, instance=user)
        registration_form = RegistrationForm(request.POST, instance=registration)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        # Валидация
        if user_form.is_valid() and registration_form.is_valid() and profile_form.is_valid():
            # Обработка пароля
            pw_current = user_form.cleaned_data.get('password_current')
            pw_new = user_form.cleaned_data.get('password_new')

            if pw_new:
                if not user.check_password(pw_current):
                    user_form.add_error('password_current', 'Current password is incorrect.')
                else:
                    user.set_password(pw_new)
                    user.save()
                    update_session_auth_hash(request, user)
            else:
                user_form.save()

            registration = registration_form.save(commit=False)
            social_title = request.POST.get('social_title')
            if social_title:
                registration.social_title = social_title  # Убедитесь, что поле social_title есть в модели
            registration.save()

            profile_form.save()

            messages.success(request, 'Your account has been updated successfully.')
            return redirect('account')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        user_form = AccountDetailsForm(instance=user)
        registration_form = RegistrationForm(instance=registration)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'registration_form': registration_form,
        'profile_form': profile_form,
    }
    return render(request, 'webapp/account/account.html', context)


@login_required
def account_edit(request):
    user = request.user

    # Получаем или создаём связанные объекты UserRegistration и UserProfile
    registration, _ = UserRegistration.objects.get_or_create(
        user_id=user.id, defaults={'name': user.get_full_name() or user.username, 'email': user.email}
    )
    profile, _ = UserProfile.objects.get_or_create(registration=registration)

    if request.method == 'POST':
        user_form = AccountDetailsForm(request.POST, instance=user)
        registration_form = RegistrationForm(request.POST, instance=registration)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and registration_form.is_valid() and profile_form.is_valid():
            # Обработка смены пароля
            pw_current = user_form.cleaned_data.get('password_current')
            pw_new = user_form.cleaned_data.get('password_new')

            if pw_new:
                if not user.check_password(pw_current):
                    user_form.add_error('password_current', 'Current password is incorrect.')
                else:
                    user.set_password(pw_new)
                    user.save()
                    update_session_auth_hash(request, user)
            else:
                user_form.save()

            registration_obj = registration_form.save(commit=False)
            social_title = request.POST.get('social_title')
            if social_title:
                registration_obj.social_title = social_title  # Добавьте поле social_title в модель, если его нет
            registration_obj.save()

            profile_form.save()

            messages.success(request, 'Your account has been updated successfully.')
            return redirect('account_edit')  # или на другую страницу по желанию
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        user_form = AccountDetailsForm(instance=user)
        registration_form = RegistrationForm(instance=registration)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'registration_form': registration_form,
        'profile_form': profile_form,
    }
    return render(request, 'webapp/account/account_edit.html', context)


@login_required
def account_settings(request):
    user = request.user

    # Получаем или создаём связанные модели
    registration, _ = UserRegistration.objects.get_or_create(
        user_id=user.id, defaults={'name': user.get_full_name() or user.username, 'email': user.email}
    )
    profile, _ = UserProfile.objects.get_or_create(registration=registration)

    if request.method == 'POST':
        user_form = AccountDetailsForm(request.POST, instance=user)
        registration_form = RegistrationForm(request.POST, instance=registration)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and registration_form.is_valid() and profile_form.is_valid():
            # Обработка смены пароля
            pw_current = user_form.cleaned_data.get('password_current')
            pw_new = user_form.cleaned_data.get('password_new')

            if pw_new:
                if not user.check_password(pw_current):
                    user_form.add_error('password_current', 'Current password is incorrect.')
                else:
                    user.set_password(pw_new)
                    user.save()
                    update_session_auth_hash(request, user)
            else:
                user_form.save()

            # Сохраняем регистрацию
            registration_obj = registration_form.save(commit=False)
            social_title = request.POST.get('social_title')
            if social_title:
                registration_obj.social_title = social_title  # Убедитесь, что такое поле есть в модели
            registration_obj.save()

            # Сохраняем профиль
            profile_form.save()

            messages.success(request, 'Your account settings have been updated successfully.')
            return redirect('account_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = AccountDetailsForm(instance=user)
        registration_form = RegistrationForm(instance=registration)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'registration_form': registration_form,
        'profile_form': profile_form,
    }
    return render(request, 'webapp/account/account_settings.html', context)
