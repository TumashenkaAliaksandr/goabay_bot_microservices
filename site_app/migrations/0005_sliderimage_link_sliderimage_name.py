# Generated by Django 5.1.5 on 2025-02-14 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_app', '0004_sliderimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='sliderimage',
            name='link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sliderimage',
            name='name',
            field=models.CharField(default='slider', max_length=100),
        ),
    ]
