# Generated by Django 5.1.5 on 2025-02-01 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0025_alter_news_name_alter_news_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='words',
            name='word_gender',
            field=models.CharField(choices=[('Отлично', 'Неприлично'), ('Да', 'Нет'), ('Гоа', 'И что?')], max_length=7, verbose_name='Gender'),
        ),
    ]
