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


