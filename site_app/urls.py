from django.urls import path
from django.conf.urls.static import static
from goabay_bot import settings
from . import views
from .views import news, about, contact, cart, wishlist, checkout, shop, product, compare, account, forgot_password, \
    login, registrations

urlpatterns = [
    path('', views.index, name='home'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('news/', news, name='news'),
    path('about/', about, name='about'),
    path('wishlist/', wishlist, name='wishlist'),
    path('compare/', compare, name='compare'),
    path('shop/', shop, name='shop'),
    path('product/', product, name='product'),
    path('checkout/', checkout, name='checkout'),
    path('cart/', cart, name='cart'),
    path('contacts/', contact, name='contacts'),
    path('account/', account, name='account'),
    path('login/', login, name='login'),
    path('registrations/', registrations, name='registrations'),
    path('forgot-password/', forgot_password, name='forgot-password'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
