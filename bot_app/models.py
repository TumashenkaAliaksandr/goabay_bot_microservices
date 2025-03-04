import re

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from site_app.models import Category
from django.utils.text import slugify


class Words(models.Model):

    gender = {
        ('Гоа', 'И что?'),
        ('Да', 'Нет'),
        ('Отлично', 'Неприлично'),
    }
    word = models.CharField(verbose_name="Word", max_length=100, default='')
    word_gender = models.CharField(verbose_name="Gender", max_length=7, choices=gender)

    def __str__(self):
        return self.word_gender + " " + self.word


class UserRegistration(models.Model):
    user_id = models.IntegerField(unique=True)  # ID пользователя Telegram
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    step = models.CharField(max_length=50, blank=True, null=True)  # Текущий шаг регистрации
    is_registered = models.BooleanField(default=False)

    def __str__(self):
        return f"Registration for user {self.user_id}"


class Product(models.Model):
    """Продукты в каталоге"""
    name = models.CharField(max_length=200, db_index=True, default='Название')
    slug = models.SlugField(max_length=200, db_index=True, unique=True, default='default-slug')
    image = models.ImageField(upload_to='products', verbose_name='photo', null=True, blank=True)
    desc = models.TextField(blank=True, default='Описание')  # Основное описание продукта
    additional_description = models.TextField(blank=True, null=True)  # Дополнительное описание продукта
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    rating = models.CharField(max_length=5, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True)  # Поле для скидки
    category = models.ManyToManyField(Category, related_name='products')

    # Новые поля для размеров и литров
    sizes = models.CharField(max_length=100, blank=True)  # Размеры (например: S, M, L)
    volume_liters = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Объем в литрах

    brand = models.CharField(max_length=100, blank=True, default='Unknown')  # Бренд продукта
    capacity = models.CharField(max_length=100, blank=True)  # Вместимость
    color = models.CharField(max_length=50, blank=True)  # Цвет
    material_up = models.CharField(max_length=100, blank=True)  # Верхний материал
    power_source = models.CharField(max_length=100, blank=True)  # Источник питания
    material = models.CharField(max_length=100, blank=True)  # Материал
    quantity = models.PositiveIntegerField(default=0)
    show_quantity = models.BooleanField(default=False)

    is_popular = models.BooleanField(verbose_name='Популярные', default=False, blank=True)
    is_brand = models.BooleanField(verbose_name='Имя Бренда', default=False, blank=True)
    is_index = models.BooleanField(verbose_name='На главную', default=False, blank=True)
    is_site_bar = models.BooleanField(verbose_name='В сайт Бар', default=False, blank=True)
    is_not_stock = models.BooleanField(verbose_name='Нет в наличии', default=False, blank=True)
    is_sale = models.BooleanField(verbose_name='Акции - Распродажи', default=False, blank=True)
    is_new_product = models.BooleanField(verbose_name='Новинки', default=False, blank=True)
    is_main_slider = models.BooleanField(verbose_name='В главный слайдер', default=False, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # Очищаем slug от лишних символов
        cleaned_slug = re.sub(r'[^\w\s-]', '', self.slug).strip().replace(' ', '-').lower()

        # Используем только cleaned_slug в URL
        return reverse('product_detail', args=[cleaned_slug])


class ProductImage(models.Model):
    """Дополнительные изображения продукта"""
    product = models.ForeignKey(Product, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/additional/', verbose_name='Дополнительное изображение')

    class Meta:
        verbose_name = 'ДопИзо Товара'
        verbose_name_plural = 'ДопИзо Товара'

    def __str__(self):
        return f"{self.product.name} - ДопИзо Товара"


class News(models.Model):
    """Модель для новостей"""
    name = models.CharField(max_length=200, db_index=True)  # Название новости
    slug = models.SlugField(max_length=200, db_index=True, unique=True, blank=True)  # Слаг
    description = models.TextField(blank=True)  # Описание новости
    date = models.DateTimeField(auto_now_add=True)  # Дата новости

    class Meta:
        ordering = ('-date',)
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('news_detail', args=[self.id, self.slug])

class NewsImage(models.Model):
    """Модель для изображений новостей"""
    news = models.ForeignKey(News, related_name='news_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news_photos/')
    description = models.CharField(max_length=255, default="Default description")  # Описание изображения

    class Meta:
        verbose_name = "Изображение новости"
        verbose_name_plural = "Изображения новостей"

    def __str__(self):
        return f"Изображение для {self.news.name} - {self.description}"


class AboutUs(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='about_photos/', blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'О нас'
        verbose_name_plural = 'стр.О нас'
