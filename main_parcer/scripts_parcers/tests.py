import os
import sys
import time
import django

# 1. Указываем путь к корню проекта (где лежит settings.py)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)

# 2. Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goabay_bot.settings')  # замените на ваш путь

# 3. Инициализируем Django
django.setup()

# 4. Импортируем модели и функции после инициализации
from site_app.models import Brand
from bot_app.models import Product, ProductVariant
from main_parcer.scripts_parcers.puma import save_to_csv, save_to_json

# --- Тестовые данные ---
test_products = [
    {
        'random_id': 'PRODVAR01',
        'product_name': 'Puma UltraRide Sneakers',
        'brand': 'Puma',
        'product_url': 'https://example.com/puma-ultraride',
        'main_category': 'Shoes',
        'subcategories': 'Sneakers / Men',
        'sale_price': '4999',
        'original_price': '5999',
        'description': 'Lightweight running sneakers for men.',
        'product_type': 'variative',
        'variations': [
            {
                'color': 'Red',
                'sizes': ['41', '42', '43'],
                'main_image': 'https://example.com/img/red-main.jpg',
                'all_images': [
                    'https://example.com/img/red-main.jpg',
                    'https://example.com/img/red-side.jpg'
                ]
            },
            {
                'color': 'Blue',
                'sizes': ['40', '41'],
                'main_image': 'https://example.com/img/blue-main.jpg',
                'all_images': [
                    'https://example.com/img/blue-main.jpg',
                    'https://example.com/img/blue-side.jpg'
                ]
            }
        ]
    },
    {
        'random_id': 'PRODSIMPLE01',
        'product_name': 'Puma Classic Cap',
        'brand': 'Puma',
        'product_url': 'https://example.com/puma-cap',
        'main_category': 'Accessories',
        'subcategories': 'Caps / Unisex',
        'sale_price': '999',
        'original_price': '',
        'description': 'Classic unisex cap for everyday use.',
        'product_type': 'simple',
        'variations': []
    },
]

# --- Функция сохранения в базу ---
def save_products_to_db(products):
    from django.db import transaction
    from django.utils.text import slugify

    with transaction.atomic():
        for prod in products:
            slug = prod['random_id']
            brand_slug = slugify(prod['brand'])
            brand_obj, _ = Brand.objects.get_or_create(
                slug=brand_slug,
                defaults={'name': prod['brand']}
            )

            product, created = Product.objects.get_or_create(slug=slug, defaults={
                'name': prod['product_name'],
                'brand': brand_obj,
                'desc': prod.get('description', ''),
                # Добавьте остальные поля модели Product, если нужно
            })
            if not created:
                # Обновляем поля, если изменились
                product.name = prod['product_name']
                product.brand = brand_obj
                product.desc = prod.get('description', '')
                product.save()

            # Сохраняем вариации
            for var in prod.get('variations', []):
                color = var.get('color', '')
                sizes = var.get('sizes', [])
                variant, v_created = ProductVariant.objects.get_or_create(
                    product=product,
                    color=color,
                    defaults={
                        'price': prod.get('sale_price'),
                        'size': sizes,
                        # Добавьте остальные поля модели варианта, если нужно
                    }
                )
                if not v_created:
                    variant.price = prod.get('sale_price')
                    variant.size = sizes
                    variant.save()

# --- Функция проверки сохранения в базу ---
def check_db_save(products):
    success = True
    for prod in products:
        slug = prod['random_id']
        try:
            product = Product.objects.get(slug=slug)
            print(f"✅ Найден продукт в БД: {product.name} (slug={slug})")
            for var in prod.get('variations', []):
                color = var.get('color', '')
                if not ProductVariant.objects.filter(product=product, color=color).exists():
                    print(f"❌ Вариация с цветом '{color}' не найдена для продукта {slug}")
                    success = False
                else:
                    print(f"   ✅ Вариация с цветом '{color}' найдена")
        except Product.DoesNotExist:
            print(f"❌ Продукт с slug={slug} не найден в БД")
            success = False
    return success

# --- Главная функция теста ---
def main():
    csv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'csv_files')
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    csv_path = os.path.join(csv_dir, 'test-puma-products.csv')
    json_path = os.path.join(csv_dir, 'jsons_files/test-puma-products.json')

    print("Сохраняем тестовые данные в CSV...")
    start = time.time()
    save_to_csv(test_products, filename=csv_path)
    print(f"save_to_csv выполнена за {time.time() - start:.4f} секунд")

    print("Сохраняем тестовые данные в JSON...")
    start = time.time()
    save_to_json(test_products, filename=json_path)
    print(f"save_to_json выполнена за {time.time() - start:.4f} секунд")

    print("\nСохраняем тестовые данные в базу данных...")
    start = time.time()
    save_products_to_db(test_products)
    print(f"save_products_to_db выполнена за {time.time() - start:.4f} секунд")

    print("\nПроверяем сохранение в базу данных...")
    if check_db_save(test_products):
        print("✅ Все товары и вариации успешно сохранены в БД")
    else:
        print("❌ Ошибки при сохранении товаров или вариаций в БД")

    print(f"\nПроверьте файлы:\n  CSV:  {csv_path}\n  JSON: {json_path}")

if __name__ == '__main__':
    main()
