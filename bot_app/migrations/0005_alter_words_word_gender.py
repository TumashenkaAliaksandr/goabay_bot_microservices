# Generated by Django 5.0.6 on 2024-06-10 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0004_alter_words_word_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='words',
            name='word_gender',
            field=models.CharField(choices=[('Да', 'Нет'), ('Гоа', 'И что?'), ('Отлично', 'Неприлично')], max_length=7, verbose_name='Gender'),
        ),
    ]
