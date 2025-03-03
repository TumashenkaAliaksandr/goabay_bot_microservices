# Generated by Django 5.1.5 on 2025-03-03 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0042_alter_words_word_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='words',
            name='word_gender',
            field=models.CharField(choices=[('Гоа', 'И что?'), ('Отлично', 'Неприлично'), ('Да', 'Нет')], max_length=7, verbose_name='Gender'),
        ),
    ]
