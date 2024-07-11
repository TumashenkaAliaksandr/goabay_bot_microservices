# Generated by Django 5.0.6 on 2024-06-10 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='words',
            name='word_gender',
            field=models.CharField(choices=[('Да', 'Нет'), ('Отлично', 'Неприлично'), ('Гоа', 'И что?')], max_length=7, verbose_name='Gender'),
        ),
    ]