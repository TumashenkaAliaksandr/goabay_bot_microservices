from django.db import models


class Category(models.Model):
    """Категории продуктов"""
    name = models.CharField(max_length=200, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

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
