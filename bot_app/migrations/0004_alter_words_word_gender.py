# Generated by Django 5.0.6 on 2024-06-10 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0003_alter_words_word_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='words',
            name='word_gender',
            field=models.CharField(choices=[('Гоа', 'И что?'), ('Да', 'Нет'), ('Отлично', 'Неприлично')], max_length=7, verbose_name='Gender'),
        ),
    ]
