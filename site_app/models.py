from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from bot_app.models import Product


class Category(models.Model):
    """Категории продуктов"""
    name = models.CharField(max_length=200)  # Убрали unique=True
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='subcategories'
    )

    def get_all_subcategories(self):
        """Рекурсивно получаем все подкатегории"""
        subcategories = list(self.subcategories.all())
        for subcategory in self.subcategories.all():
            subcategories.extend(subcategory.get_all_subcategories())
        return subcategories

    def get_all_products(self):
        """Все товары в этой категории и подкатегориях"""
        from django.db.models import Q
        categories = [self] + self.get_all_subcategories()
        return Product.objects.filter(category__in=categories).distinct()

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        unique_together = ('name', 'parent')  # Теперь уникальность учитывает родителя

    def __str__(self):
        return self.name




class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    permission = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Подписка (всплывающее окно)'
        verbose_name_plural = 'Подписка (всплывающее окно)'


class Brand(models.Model):
    name = models.CharField(max_length=100, default='brand', unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='brands_logo_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    brand_id = models.IntegerField(default=0)
    link = models.URLField(blank=True, null=True)

    def get_products_by_category(self, category):
        """Товары бренда в конкретной категории"""
        return self.brands.filter(category=category)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Бренды'
        verbose_name_plural = 'Бренды'

# Сигнал для автоматического формирования слага
@receiver(pre_save, sender=Brand)
def create_slug(sender, instance, *args, **kwargs):
    if not instance.slug or instance.slug == 'default-slug':
        instance.slug = slugify(instance.name)


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Тег')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class SocialNetwork(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название соцсети")
    icon = models.ImageField(upload_to='social_icons/', verbose_name="Иконка")
    url = models.URLField(verbose_name="Ссылка")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Социальная сеть"
        verbose_name_plural = "Социальные сети"
