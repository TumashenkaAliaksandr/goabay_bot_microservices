from django.apps import apps
from django.contrib.auth.models import User, Group
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from bot_app import models
from site_app.admin import ProductImageInline
from .models import Product, News, NewsImage
from .forms import ProductForm


# Создаём экземпляр кастомной админки
class MyAdminSite(AdminSite):
    """Кастомная админ-панель"""
    site_header = "🐘 ॐ नम: शिवाय  GoaBay админ панель"
    site_title = "Управление сайтом"
    index_title = "Добро пожаловать в GoaBay админ!"

admin_site = MyAdminSite(name="myadmin")

# Удаляем стандартную регистрацию модели User и Group
for model in [User, Group]:
    try:
        admin.site.unregister(model)  # Сначала разрегистрируем, если уже есть
    except admin.sites.NotRegistered:
        pass  # Если модель не была зарегистрирована, просто пропускаем

# Теперь можно зарегистрировать модель User в кастомной админке
class CustomUserAdmin(BaseUserAdmin):
    # Здесь можно переопределить настройки админки для User
    pass

admin_site.register(User, CustomUserAdmin)
admin_site.register(Group)  # Регистрация группы в кастомной админке

# Автоматическая регистрация всех моделей проекта, кроме User и Group
all_models = apps.get_models()

for model in all_models:
    if model not in [User, Group]:  # Пропускаем уже зарегистрированные модели
        try:
            admin_site.register(model)
        except admin.sites.AlreadyRegistered:
            pass  # Пропускаем уже зарегистрированные модели


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


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1
    fields = ("image", "description", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="auto" />')
        return "Нет изображения"

    preview.short_description = "Превью"

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "date")
    search_fields = ("title", "description")
    ordering = ("-date",)
    inlines = [NewsImageInline]