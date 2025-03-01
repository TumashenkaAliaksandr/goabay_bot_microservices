from __future__ import absolute_import, unicode_literals

# Это важно для того, чтобы Celery стартовал с настройками Django
from .celery import app as celery_app

__all__ = ('celery_app',)
