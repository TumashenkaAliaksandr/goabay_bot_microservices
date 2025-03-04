from django.apps import apps
from django.contrib.auth.models import User, Group
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from site_app.admin import ProductImageInline
from site_app.forms import ProductForm
from . import models  # Убедитесь, что импортируете правильно
from .models import Product, News, NewsImage, AboutUs  # Убедитесь, что импортируете правильно

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
    if model not in [User, Group, Product, News]:  # Исключаем Product и News
        try:
            admin_site.register(model)
        except admin.sites.AlreadyRegistered:
            pass  # Пропускаем уже зарегистрированные модели

# class WordAdmin(admin.ModelAdmin):
#     list_display = ['pk', 'word_gender', 'word']
#     list_edit = ['word_gender', 'word']
#
# admin_site.register(models.Words, WordAdmin)

class ProductAdmin(admin.ModelAdmin):
    # Используем кастомную форму для TinyMCE
    form = ProductForm

    # Поля, отображаемые в списке продуктов
    list_display = ('name', 'price', 'is_popular', 'is_new_product', 'has_additional_description', 'image_preview')

    # Фильтрация по полям
    list_filter = ('category', 'brand', 'is_popular', 'is_new_product')

    # Поля для поиска
    search_fields = ('name', 'desc')

    # Автоматическое заполнение поля slug на основе названия продукта
    prepopulated_fields = {'slug': ('name',)}

    # Встраиваемая модель для изображений продукта
    inlines = [ProductImageInline]

    def image_preview(self, obj):
        """Метод для отображения предварительного просмотра изображения в админке."""
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return '-'

    image_preview.short_description = 'Image Preview'  # Заголовок для колонки

    def has_additional_description(self, obj):
        """Метод для отображения галочки, если есть additional_description."""
        return bool(obj.additional_description)

    has_additional_description.short_description = 'Additional Description'  # Заголовок для колонки
    has_additional_description.boolean = True  # Чтобы Django отображал как булево значение

    def save_model(self, request, obj, form, change):
        """Метод для обработки сохранения модели."""
        obj.additional_description = form.cleaned_data['additional_description']  # Сохраняем данные из TinyMCE
        super().save_model(request, obj, form, change)


# Регистрируем ProductAdmin в кастомной админке
admin_site.register(Product, ProductAdmin)

class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1

class NewsAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'slug')  # Поля, отображаемые в списке
    prepopulated_fields = {'slug': ('name',)}  # Автоматическое заполнение slug на основе названия
    search_fields = ('name', 'description')  # Поля для поиска
    ordering = ('-date',)  # Порядок сортировки, по дате новостей
    list_filter = ('date',)  # Фильтры для боковой панели, по дате

    def save_model(self, request, obj, form, change):
        """Метод для обработки сохранения модели"""
        super().save_model(request, obj, form, change)

admin_site.register(News, NewsAdmin)  # Регистрируем NewsAdmin в кастомной админке

# class AboutUsAdmin(admin.ModelAdmin):
#     list_display = ('title', 'created_at', 'updated_at')
#     search_fields = ('title',)
#
# admin_site.register(AboutUs, AboutUsAdmin)  # Регистрируем AboutUsAdmin в кастомной админке
