from django.db import models


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
    name = models.CharField(max_length=255, blank=True, null=True)
    name = models.TextField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price', default=0.00)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Services"
        verbose_name_plural = "Services"
