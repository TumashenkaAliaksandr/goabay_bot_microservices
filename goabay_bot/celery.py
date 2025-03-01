from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goabay_bot.settings')

app = Celery('goabay_bot')

# Настройка для брокера и backend
app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0'
)

# Здесь может быть список задач Celery
app.conf.task_routes = {
    'goabay_bot.tasks.*': {'queue': 'celery'},
}

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
