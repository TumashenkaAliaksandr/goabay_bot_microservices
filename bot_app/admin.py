from django.contrib import admin
from django.utils.safestring import mark_safe

from bot_app import models
from .models import Product
from .forms import ProductForm

class WordAdmin(admin.ModelAdmin):
    list_display = ['pk', 'word_gender', 'word']
    list_edit = ['word_gender', 'word']


admin.site.register(models.Words, WordAdmin)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ('name', 'price', 'image')  # Поля, отображаемые в списке
    search_fields = ('name',)  # Поля для поиска
    list_filter = ('price',)  # Фильтры по цене

    # Дополнительные настройки, если необходимо
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="100" />')
        return '-'

    image_preview.short_description = 'Image Preview'
