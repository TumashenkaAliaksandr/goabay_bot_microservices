from django.core.management.base import BaseCommand
from site_app.tasks import update_ishalife_products  # Импортируем задачу Celery

class Command(BaseCommand):
    help = "Обновляет список товаров"

    def handle(self, *args, **kwargs):
        self.stdout.write("Запуск обновления товаров...")
        result = update_ishalife_products.delay()  # Запускаем задачу через Celery

        # Логирование ID задачи
        self.stdout.write(f"Задача на обновление товаров добавлена в очередь Celery с ID: {result.id}")
