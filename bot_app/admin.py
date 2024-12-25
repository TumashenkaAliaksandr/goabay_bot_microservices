from django.contrib import admin
from django.utils.safestring import mark_safe

from bot_app import models
from site_app.admin import ProductImageInline
from .models import Product
from .forms import ProductForm


class WordAdmin(admin.ModelAdmin):
    list_display = ['pk', 'word_gender', 'word']
    list_edit = ['word_gender', 'word']


admin.site.register(models.Words, WordAdmin)


# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     form = ProductForm
#     list_display = ('name', 'price', 'image_preview', 'brand', 'category')  # Добавлено поле brand
#     search_fields = ('name', 'brand')  # Поля для поиска (добавлено поле brand)
#     list_filter = ('price', 'brand')  # Фильтры по цене и бренду
#
#     def image_preview(self, obj):
#         if obj.image:
#             return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
#         return '-'
#
#     image_preview.short_description = 'Image Preview'
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_popular', 'is_new_product', 'image_preview')  # Отображаем нужные поля
    list_filter = ('category', 'brand', 'is_popular', 'is_new_product')  # Фильтрация по полям
    search_fields = ('name', 'desc')  # Поиск по имени и описанию
    prepopulated_fields = {'slug': ('name',)}  # Автоматическое заполнение поля slug
    inlines = [ProductImageInline]

    def image_preview(self, obj):
        """Метод для отображения предварительного просмотра изображения в админке."""
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return '-'

    image_preview.short_description = 'Image Preview'  # Заголовок для колонки

    def save_model(self, request, obj, form, change):
        """Метод для обработки сохранения модели."""
        super().save_model(request, obj, form, change)

admin.site.register(Product, ProductAdmin)
