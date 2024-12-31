from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt

from site_app import views

urlpatterns = [
    path('', csrf_exempt(views.index), name='index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
