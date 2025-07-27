from django.urls import path

from site_app.views import ProductListCreateAPIView, ProductRetrieveUpdateDestroyAPIView

urlpatterns = [
    # GET список продуктов и POST создание
    path('api/products/', ProductListCreateAPIView.as_view(), name='api_product_list_create'),

    # GET/PUT/PATCH/DELETE конкретного продукта по слагу
    path('api/products/<slug:slug>/', ProductRetrieveUpdateDestroyAPIView.as_view(), name='api_product_detail'),
]
