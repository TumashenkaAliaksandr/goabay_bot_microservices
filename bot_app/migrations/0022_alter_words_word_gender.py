# Generated by Django 5.1.5 on 2025-02-01 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0021_alter_news_options_alter_newsimage_options_news_slug_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='words',
            name='word_gender',
            field=models.CharField(choices=[('Гоа', 'И что?'), ('Да', 'Нет'), ('Отлично', 'Неприлично')], max_length=7, verbose_name='Gender'),
        ),
    ]
