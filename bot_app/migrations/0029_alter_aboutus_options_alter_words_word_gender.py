# Generated by Django 5.1.5 on 2025-02-03 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0028_aboutus_image_alter_words_word_gender'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aboutus',
            options={'verbose_name': 'О нас', 'verbose_name_plural': 'стр.О нас'},
        ),
        migrations.AlterField(
            model_name='words',
            name='word_gender',
            field=models.CharField(choices=[('Да', 'Нет'), ('Гоа', 'И что?'), ('Отлично', 'Неприлично')], max_length=7, verbose_name='Gender'),
        ),
    ]
