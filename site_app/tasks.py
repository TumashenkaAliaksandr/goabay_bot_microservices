from celery import shared_task
import logging
from datetime import datetime
from bot_app.models import Product
from django.core.cache import cache

# Настройка логгера
logger = logging.getLogger(__name__)

@shared_task
def update_ishalife_products():
    logger.info(f"Обновление товаров запущено в {datetime.now()}...")

    updated_products = []  # Список обновленных товаров
    deleted_products = []  # Список удаленных товаров

    # Логика обновления товаров
    for product in Product.objects.all():
        old_price = product.price
        new_price = old_price + 10  # Пример: увеличиваем цену на 10

        if old_price != new_price:
            product.price = new_price
            product.save()
            updated_products.append(product.name)

    # Логирование обновлений
    if updated_products:
        logger.info(f"Обновленные товары: {', '.join(updated_products)}")

    # Логика удаления товаров (например, если цена равна 0)
    for product in Product.objects.filter(price=0):
        deleted_products.append(product.name)
        product.delete()

    # Логирование удаленных товаров
    if deleted_products:
        logger.info(f"Удаленные товары: {', '.join(deleted_products)}")

    # Очистка кеша после обновлений
    cache.delete('ishalife_products')

    logger.info(f"Обновление товаров завершено в {datetime.now()}.")
    logger.info(f"Обновлено товаров: {len(updated_products)}, удалено товаров: {len(deleted_products)}")

    return "Обновление товаров завершено!"
