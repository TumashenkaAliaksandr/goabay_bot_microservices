from django.urls import path
from django.conf.urls.static import static
from . import views
from django.conf import settings
from .views import news, cart, checkout, shop, product, compare, account, forgot_password, \
    login, registrations, four_zero_four, product_catalog, brand, elephant, bestsellers, handmade, \
    brand_name, products_brands

urlpatterns = [
    path('', views.index, name='home'),
    path('product/<slug:slug>/<str:name>/', views.product_detail, name='product_detail'),
    path('brand', brand, name='brand'),
    path('products-brands/', products_brands, name='products-brands'),
    path('brand-name/<slug:slug>/', brand_name, name='brand-name'),
    path('brand/<slug:slug>/<str:name>/', views.single_brand, name='single_brand'),
    path('best-sellers/', bestsellers, name='best-sellers'),
    path('news/', news, name='news'),
    path('hand-made/', handmade, name='hand-made'),
    path('compare/', compare, name='compare'),
    path('shop/', shop, name='shop'),
    path('product/', product, name='product'),
    path('buy-elephant/', elephant, name='buy-elephant'),
    path('product-catalog/', product_catalog, name='product-catalog'),
    # path('isha_bestsellers_products.json/', views.serve_json, name='serve_json'),
    path('brand/isha-life/', views.update_ishalife_products, name='isha_life_page'),
    path('archive/', views.archive, name='archive'),
    path('category/<str:category_name>/', views.category_view, name='category'),
    path('checkout/', checkout, name='checkout'),
    path('cart/', cart, name='cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('account/', account, name='account'),
    path('login/', login, name='login'),
    path('registrations/', registrations, name='registrations'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('404/', four_zero_four, name='four-zero-four'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
