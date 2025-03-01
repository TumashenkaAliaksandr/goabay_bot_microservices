from django.urls import path
from django.conf.urls.static import static
from goabay_bot import settings
from . import views
from .views import news, about, contact, cart, wishlist, checkout, shop, product, compare, account, forgot_password, \
    login, registrations, four_zero_four, product_catalog, how_we_work, brand, elephant, bestsellers, handmade

urlpatterns = [
    path('', views.index, name='home'),
    path('product/<slug:slug>/<str:name>/', views.product_detail, name='product_detail'),
    path('brand/', brand, name='brand'),
    path('best-sellers/', bestsellers, name='best-sellers'),
    path('brand/<slug:slug>/<str:name>/', views.single_brand, name='single_brand'),
    path('news/', news, name='news'),
    path('hand-made/', handmade, name='hand-made'),
    path('about/', about, name='about'),
    path('wishlist/', wishlist, name='wishlist'),
    path('compare/', compare, name='compare'),
    path('shop/', shop, name='shop'),
    path('product/', product, name='product'),
    path('buy-elephant/', elephant, name='buy-elephant'),
    path('product-catalog/', product_catalog, name='product-catalog'),
    path('isha_bestsellers_products.json/', views.serve_json, name='serve_json'),
    path('brand/isha-life/', views.update_ishalife_products, name='isha_life_page'),
    path('category/<str:category_name>/', views.category_view, name='category'),
    path('how-we-work/', how_we_work, name='how-we-work'),
    path('checkout/', checkout, name='checkout'),
    path('cart/', cart, name='cart'),
    path('contacts/', contact, name='contacts'),
    path('account/', account, name='account'),
    path('login/', login, name='login'),
    path('registrations/', registrations, name='registrations'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('404/', four_zero_four, name='four-zero-four'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
