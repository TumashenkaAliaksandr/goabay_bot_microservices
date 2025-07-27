from django.contrib import admin
from django.urls import path, include
from bot_app.admin import admin_site
from site_app.views import ProductListCreateAPIView  # или из api_views, если разделяете

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("goabay-admin/", admin_site.urls),
    path('', include('site_app.urls')),
    path('tinymce/', include('tinymce.urls')),

    path('api/products/', ProductListCreateAPIView.as_view(), name='api_product_list_create'),
]
