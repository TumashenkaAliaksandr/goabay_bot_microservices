from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    # AJAX
    path('ajax/variant-images/<int:product_id>/<str:color>/', views.get_variant_images, name='get_variant_images'),

    # Аккаунт и аутентификация
    path('account/', views.account, name='account'),
    path('account/edit/', views.account_edit, name='account_edit'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('registrations/', views.registrations, name='registrations'),

    # Архив, новости, контакты
    path('archive/', views.archive, name='archive'),
    path('best-sellers/', views.bestsellers, name='best-sellers'),
    path('contacts/', views.newsletter_signup, name='contacts'),  # Проверьте, правильная ли вьюха
    path('hand-made/', views.handmade, name='hand-made'),
    path('news/', views.news, name='news'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),

    # Бренды
    path('brand/', views.brand, name='brand'),  # Список брендов
    path('brand/<slug:slug>/', views.single_brand, name='single_brand'),  # Детальная страница бренда (исправлено)
    path('brand-name/<slug:slug>/', views.products_brands, name='brand-name'),  # AJAX/совместимость
    path('brand/isha-life/', views.update_ishalife_products, name='isha_life_page'),  # Спец. страница бренда

    # Категории и каталог
    path('category/<str:category_name>/', views.category_view, name='category'),
    path('compare/', views.compare, name='compare'),
    path('product-catalog/', views.product_catalog, name='product-catalog'),

    # Главная и магазин
    path('', views.index, name='home'),
    path('product/', views.product, name='product'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('products-brands/', views.products_brands, name='products-brands'),

    # Покупка слона
    path('buy-elephant/', views.elephant, name='buy-elephant'),

    # Магазин
    path('shop/', views.shop, name='shop'),

    # Оплата
    path('payment/', views.payments, name='payment'),

    # 404
    path('404/', views.four_zero_four, name='four-zero-four'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
