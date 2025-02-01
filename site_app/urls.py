from django.urls import path
from django.conf.urls.static import static
from goabay_bot import settings
from . import views
from .views import news, about, contact

urlpatterns = [
    path('', views.index, name='home'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('news', news, name='news'),
    path('about', about, name='about'),
    path('contacts', contact, name='contacts'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
