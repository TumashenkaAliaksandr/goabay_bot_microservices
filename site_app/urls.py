from django.urls import path
from django.conf.urls.static import static
from . import views
from django.conf import settings

urlpatterns = [
    # Основные маршруты
    path('', views.index, name='home'),
    path('account/', views.account, name='account'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # Маршруты для брендов
    path('brand', views.brand, name='brand'),  # Список всех брендов
    path('brand/<slug:slug>/<str:name>/', views.single_brand, name='single_brand'),  # Детальная страница бренда
    path('brand-name/<slug:slug>/', views.products_brands, name='brand-name'),  # Новое имя для AJAX-совместимости

    # Устаревшие маршруты (можно удалить после рефакторинга)
    path('products-brands/', views.products_brands, name='products-brands'),  # Оставьте только если используется
    path('brand/isha-life/', views.update_ishalife_products, name='isha_life_page'),  # Специфичный маршрут

    # Остальные маршруты
    path('best-sellers/', views.bestsellers, name='best-sellers'),
    path('news/', views.news, name='news'),
    path('hand-made/', views.handmade, name='hand-made'),
    path('compare/', views.compare, name='compare'),
    path('shop/', views.shop, name='shop'),
    path('payment/', views.payments, name='payment'),
    path('product/', views.product, name='product'),
    path('buy-elephant/', views.elephant, name='buy-elephant'),
    path('product-catalog/', views.product_catalog, name='product-catalog'),
    path('archive/', views.archive, name='archive'),
    path('category/<str:category_name>/', views.category_view, name='category'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('account/', views.account, name='account'),
    path('login/', views.login, name='login'),
    path('registrations/', views.registrations, name='registrations'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('404/', views.four_zero_four, name='four-zero-four'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
    path('contacts/', views.newsletter_signup, name='contacts'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
