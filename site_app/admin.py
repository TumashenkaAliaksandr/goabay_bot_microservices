from django.contrib import admin

from bot_app.models import ProductImage, Product
from site_app.models import Category, SliderImage


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')  # Отображаем имя и родительскую категорию
    list_filter = ('parent',)  # Фильтрация по родительской категории
    search_fields = ('name',)  # Поиск по имени категории


# Регистрация модели Category с настройками админки
admin.site.register(Category, CategoryAdmin)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Количество пустых форм для добавления новых изображений


admin.site.register(ProductImage)

@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'image', 'created_at', 'link']
    ordering = ['-created_at']

