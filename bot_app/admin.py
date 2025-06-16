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
    form = ProductForm

    list_display = (
        'name', 'sku', 'price', 'stock_status', 'quantity', 'show_quantity',
        'is_popular', 'is_new_product', 'is_sale', 'image_preview', 'has_additional_description'
    )
    list_filter = (
        'category', 'brand', 'stock_status',
        'is_popular', 'is_new_product', 'is_sale'
    )
    search_fields = ('name', 'desc', 'sku', 'model')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'sku', 'model', 'brand', 'category', 'image', 'desc', 'additional_description', 'tags')
        }),
        ('Цены и наличие', {
            'fields': ('price', 'discount', 'stock_status', 'quantity', 'show_quantity', 'restock_date')
        }),
        ('Физические характеристики', {
            'fields': ('length', 'width', 'height', 'gross_weight', 'net_volume', 'color', 'aroma', 'material_up', 'material', 'capacity')
        }),
        ('Технические характеристики', {
            'fields': ('processor', 'internal_storage', 'screen_size', 'battery_capacity', 'resolution', 'interface', 'power_consumption')
        }),
        ('Одежда и обувь', {
            'fields': ('gender', 'age_group', 'sizes', 'clothing_fit')
        }),
        ('Косметика и бытовая химия', {
            'fields': ('skin_type', 'hair_type', 'effect', 'application_area', 'ingredients')
        }),
        ('Продукты питания', {
            'fields': ('calories', 'nutritional_value', 'organic', 'vegan', 'gluten_free', 'additives', 'shelf_life')
        }),
        ('Автотовары', {
            'fields': ('engine_type', 'fuel_type', 'vehicle_compatibility', 'transmission', 'horsepower', 'torque')
        }),
        ('Мебель и интерьер', {
            'fields': ('style',)
        }),
        ('Дополнительно', {
            'fields': ('barcode', 'upc', 'launch_date', 'energy_efficiency', 'reusability', 'eco_label')
        }),
        ('Гарантия и отзывы', {
            'fields': ('warranty_period', 'rating', 'reviews_count')
        }),
        ('Маркетинговые флаги', {
            'fields': ('is_popular', 'is_index', 'is_site_bar', 'is_sale', 'is_new_product', 'is_main_slider')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: contain;" />')
        return '-'
    image_preview.short_description = 'Превью'

    def has_additional_description(self, obj):
        return bool(obj.additional_description)
    has_additional_description.short_description = 'Доп. описание'
    has_additional_description.boolean = True

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
