# Generated by Django 5.0.6 on 2024-12-25 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0016_product_quantity_alter_words_word_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_brand',
            field=models.BooleanField(blank=True, default=False, verbose_name='Имя Бренда'),
        ),
        migrations.AlterField(
            model_name='words',
            name='word_gender',
            field=models.CharField(choices=[('Гоа', 'И что?'), ('Отлично', 'Неприлично'), ('Да', 'Нет')], max_length=7, verbose_name='Gender'),
        ),
    ]