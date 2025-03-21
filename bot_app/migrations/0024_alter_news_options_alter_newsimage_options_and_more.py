# Generated by Django 5.1.5 on 2025-02-01 15:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0023_alter_news_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='news',
            options={'ordering': ('-date',), 'verbose_name': 'Новость', 'verbose_name_plural': 'Новости'},
        ),
        migrations.AlterModelOptions(
            name='newsimage',
            options={'verbose_name': 'Изображение новости', 'verbose_name_plural': 'Изображения новостей'},
        ),
        migrations.RemoveField(
            model_name='news',
            name='title',
        ),
        migrations.AddField(
            model_name='news',
            name='name',
            field=models.CharField(db_index=True, default='Название Новости', max_length=200),
        ),
        migrations.AlterField(
            model_name='news',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='newsimage',
            name='news',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news_images', to='bot_app.news'),
        ),
        migrations.AlterField(
            model_name='words',
            name='word_gender',
            field=models.CharField(choices=[('Гоа', 'И что?'), ('Отлично', 'Неприлично'), ('Да', 'Нет')], max_length=7, verbose_name='Gender'),
        ),
    ]
