# Generated by Django 5.1.5 on 2025-06-25 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0016_alter_productvariant_color_alter_productvariant_size_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='color',
            field=models.CharField(blank=True, max_length=550, verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='product',
            name='meta_description',
            field=models.CharField(blank=True, max_length=612, null=True, verbose_name='SEO описание'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sizes',
            field=models.CharField(blank=True, max_length=300, verbose_name='Размеры (S, M, L и т.п.)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.CharField(blank=True, max_length=500, null=True, unique=True, verbose_name='Артикул (SKU)'),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='color',
            field=models.CharField(blank=True, max_length=555, verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=300, null=True, verbose_name='Цена вариации'),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='size',
            field=models.CharField(blank=True, max_length=555, verbose_name='Размер'),
        ),
        migrations.AlterField(
            model_name='words',
            name='word_gender',
            field=models.CharField(choices=[('Гоа', 'И что?'), ('Отлично', 'Неприлично'), ('Да', 'Нет')], max_length=7, verbose_name='Gender'),
        ),
    ]
