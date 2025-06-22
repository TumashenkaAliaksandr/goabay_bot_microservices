import re
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
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

    # Основные данные
    name = models.CharField(max_length=500, db_index=True, default='Название')
    slug = models.SlugField(max_length=500, db_index=True, unique=True, default='default-slug')
    sku = models.CharField(max_length=300, unique=True, null=True, blank=True, verbose_name='Артикул (SKU)')
    model = models.CharField(max_length=300, blank=True, verbose_name='Модель')
    brand = models.ForeignKey('site_app.Brand', on_delete=models.SET_NULL, null=True, blank=True, related_name='brands')
    image = models.ImageField(upload_to='products', verbose_name='Фото', null=True, blank=True)
    desc = models.TextField(blank=True, default='Описание', verbose_name='Описание')
    additional_description = models.TextField(blank=True, null=True, verbose_name='Дополнительное описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name='Цена')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, verbose_name='Скидка')

    # Общие атрибуты
    warranty_period = models.PositiveIntegerField(null=True, blank=True, help_text='Гарантия в месяцах', verbose_name='Гарантия')
    shelf_life = models.CharField(max_length=300, blank=True, verbose_name='Срок годности')
    certification = models.CharField(max_length=255, blank=True, verbose_name='Сертификаты')

    # Физические характеристики
    length = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text='Длина в см', verbose_name='Длина')
    width = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text='Ширина в см', verbose_name='Ширина')
    height = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text='Высота в см', verbose_name='Высота')
    gross_weight = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True, help_text='Вес брутто в кг', verbose_name='Вес брутто')
    net_volume = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True, help_text='Объем нетто в литрах', verbose_name='Объем нетто')
    color = models.CharField(max_length=150, blank=True, verbose_name='Цвет')
    aroma = models.CharField(max_length=300, blank=True, verbose_name='Аромат')
    material_up = models.CharField(max_length=300, blank=True, verbose_name='Материал (верхний слой)')
    material = models.CharField(max_length=300, blank=True, verbose_name='Материал')
    capacity = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=True, help_text='Ёмкость/вместимость', verbose_name='Ёмкость')

    # Технические характеристики (для электроники)
    processor = models.CharField(max_length=255, blank=True, verbose_name='Процессор')
    internal_storage = models.CharField(max_length=300, blank=True, verbose_name='Встроенная память')
    screen_size = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Диагональ экрана (дюймы)')
    battery_capacity = models.PositiveIntegerField(null=True, blank=True, verbose_name='Емкость батареи (мАч)')
    resolution = models.CharField(max_length=300, blank=True, verbose_name='Разрешение экрана')
    interface = models.CharField(max_length=255, blank=True, verbose_name='Интерфейсы (HDMI, USB и т.п.)')
    power_consumption = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, help_text='Потребляемая мощность (Вт)', verbose_name='Потребление энергии')

    # Одежда и обувь
    gender = models.CharField(max_length=20, blank=True, verbose_name='Пол')
    age_group = models.CharField(max_length=50, blank=True, verbose_name='Возрастная категория')
    sizes = models.CharField(max_length=100, blank=True, verbose_name='Размеры (S, M, L и т.п.)')
    clothing_fit = models.CharField(max_length=50, blank=True, verbose_name='Посадка (Slim, Regular, Oversize)')

    # Косметика и бытовая химия
    skin_type = models.CharField(max_length=300, blank=True, verbose_name='Тип кожи')
    hair_type = models.CharField(max_length=300, blank=True, verbose_name='Тип волос')
    effect = models.CharField(max_length=255, blank=True, verbose_name='Эффект (увлажнение, объем и т.п.)')
    application_area = models.CharField(max_length=255, blank=True, verbose_name='Область применения')
    ingredients = models.TextField(blank=True, verbose_name='Состав')

    # Продукты питания
    calories = models.PositiveIntegerField(null=True, blank=True, verbose_name='Калорийность (ккал)')
    nutritional_value = models.TextField(blank=True, verbose_name='Пищевая ценность')
    organic = models.BooleanField(default=False, verbose_name='Органический продукт')
    vegan = models.BooleanField(default=False, verbose_name='Веганский продукт')
    gluten_free = models.BooleanField(default=False, verbose_name='Без глютена')
    additives = models.TextField(blank=True, verbose_name='Добавки')

    # Автотовары
    engine_type = models.CharField(max_length=300, blank=True, verbose_name='Тип двигателя')
    fuel_type = models.CharField(max_length=300, blank=True, verbose_name='Тип топлива')
    vehicle_compatibility = models.CharField(max_length=255, blank=True, verbose_name='Совместимость с авто')
    transmission = models.CharField(max_length=300, blank=True, verbose_name='Коробка передач')
    horsepower = models.PositiveIntegerField(null=True, blank=True, verbose_name='Лошадиные силы')
    torque = models.PositiveIntegerField(null=True, blank=True, verbose_name='Крутящий момент (Нм)')

    # Мебель и интерьер
    style = models.CharField(max_length=300, blank=True, verbose_name='Стиль (лофт, модерн и т.п.)')

    # Дополнительно
    barcode = models.CharField(max_length=300, blank=True, verbose_name='Штрихкод')
    upc = models.CharField(max_length=300, blank=True, verbose_name='Уникальный код товара (UPC)')
    launch_date = models.DateField(null=True, blank=True, verbose_name='Дата выхода на рынок')
    energy_efficiency = models.CharField(max_length=50, blank=True, verbose_name='Класс энергоэффективности')
    reusability = models.BooleanField(default=False, verbose_name='Многоразовое использование')
    eco_label = models.CharField(max_length=255, blank=True, verbose_name='Экомаркировка')

    # Логистика и наличие
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    show_quantity = models.BooleanField(default=False, verbose_name='Показывать количество')
    STOCK_STATUS_CHOICES = [
        ('in_stock', 'В наличии'),
        ('out_of_stock', 'Нет в наличии'),
        ('preorder', 'Предзаказ'),
        ('discontinued', 'Снято с производства'),
    ]
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS_CHOICES, default='in_stock', verbose_name='Статус наличия')
    restock_date = models.DateField(null=True, blank=True, verbose_name='Дата поступления')

    # Рейтинг и отзывы
    rating = models.FloatField(blank=True, null=True, default=0.0, verbose_name='Средний рейтинг')
    reviews_count = models.PositiveIntegerField(default=0, verbose_name='Количество отзывов')

    # SEO
    meta_title = models.CharField(max_length=255, blank=True, null=True, verbose_name='SEO заголовок')
    meta_description = models.CharField(max_length=512, blank=True, null=True, verbose_name='SEO описание')
    tags = models.ManyToManyField('site_app.Tag', blank=True, related_name='products', verbose_name='Теги')

    # Категории
    category = models.ManyToManyField('site_app.Category', related_name='products', verbose_name='Категории')

    # Маркетинговые флаги
    is_popular = models.BooleanField(verbose_name='Популярные', default=False, blank=True)
    is_index = models.BooleanField(verbose_name='На главную', default=False, blank=True)
    is_site_bar = models.BooleanField(verbose_name='В сайт Бар', default=False, blank=True)
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
        cleaned_slug = re.sub(r'[^\w\s-]', '', self.slug).strip().replace(' ', '-').lower()
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

class ProductVariant(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='variants', verbose_name='Основной товар')
    description = models.TextField(blank=True, default='Описание', verbose_name='Описание')
    sku = models.CharField(max_length=300, unique=True, null=True, blank=True, verbose_name='Артикул вариации')
    size = models.CharField(max_length=50, blank=True, verbose_name='Размер')
    color = models.CharField(max_length=150, blank=True, verbose_name='Цвет')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name='Цена вариации')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    image = models.ImageField(upload_to='products/variants/', null=True, blank=True, verbose_name='Изображение вариации')

    class Meta:
        verbose_name = 'Вариация товара'
        verbose_name_plural = 'Вариации товара'

    def __str__(self):
        parts = [self.product.name]
        if self.color:
            parts.append(f"Цвет: {self.color}")
        if self.size:
            parts.append(f"Размер: {self.size}")
        return " | ".join(parts)



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


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    permission = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Подписка (всплывающее окно)'
        verbose_name_plural = 'Подписка (всплывающее окно)'


# Сигнал для автоматического формирования слага
@receiver(pre_save, sender='site_app.Brand')
def create_slug(sender, instance, *args, **kwargs):
    if not instance.slug or instance.slug == 'default-slug':
        instance.slug = slugify(instance.name)


class Review(models.Model):
    product_slug = models.SlugField(max_length=300, db_index=True)  # Связь с продуктом по slug
    author_name = models.CharField(max_length=100)
    review_text = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=[(i, f'{i} ⭐') for i in range(1, 6)])
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Review by {self.author_name} for {self.product_slug}'
