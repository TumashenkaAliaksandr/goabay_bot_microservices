# Generated by Django 5.0.6 on 2024-12-25 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0013_remove_product_quantity_product_show_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='show_quantity',
            field=models.BooleanField(default='0'),
        ),
        migrations.AlterField(
            model_name='words',
            name='word_gender',
            field=models.CharField(choices=[('Отлично', 'Неприлично'), ('Да', 'Нет'), ('Гоа', 'И что?')], max_length=7, verbose_name='Gender'),
        ),
    ]