
from django.urls import path
from django.conf.urls.static import static
from goabay_bot import settings
from . import views
from .views import product_detail, index

urlpatterns = [
    path('', index, name='site_app'),
    path('product/<int:id>/<slug:slug>/', product_detail, name='product_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

