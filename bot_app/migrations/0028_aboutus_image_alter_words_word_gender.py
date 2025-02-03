# Generated by Django 5.1.5 on 2025-02-03 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0027_aboutus_alter_words_word_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='aboutus',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='about_photos/'),
        ),
        migrations.AlterField(
            model_name='words',
            name='word_gender',
            field=models.CharField(choices=[('Да', 'Нет'), ('Отлично', 'Неприлично'), ('Гоа', 'И что?')], max_length=7, verbose_name='Gender'),
        ),
    ]
