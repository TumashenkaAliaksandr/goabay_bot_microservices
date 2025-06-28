import csv
import json
# -------------------
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import time
# from bs4 import BeautifulSoup
#
# # Настройки для запуска браузера без UI (headless режим)
# options = Options()
# options.add_argument("--headless")  # Для запуска без UI
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
#
# # Путь к драйверу Chrome (установите по своему пути)
# driver = webdriver.Chrome(options=options)
#
# def extract_sizes_from_page(url):
#     driver.get(url)
#     time.sleep(3)  # Ждем загрузки страницы (можно увеличить, если надо)
#
#     # Получаем исходный код страницы
#     html = driver.page_source
#
#     # Используем BeautifulSoup для парсинга страницы
#     soup = BeautifulSoup(html, 'html.parser')
#
#     # Пример: ищем все элементы с размерами (например, через data-content)
#     # Подставьте соответствующий класс или аттрибут для размеров
#     size_elements = soup.find_all('span', {'data-content': 'size-value'})
#
#     if size_elements:
#         sizes = [size.get_text(strip=True) for size in size_elements]
#         print(f"✅ Все доступные размеры: {sizes}")
#         driver.quit()
#         return sizes
#     else:
#         print("❌ Размеры не найдены на странице")
#         driver.quit()
#         return None
#
# # Пример использования
# url = "https://in.puma.com/in/en/pd/court-shatter-low-sneakers/399844?size=0240&swatch=04"
# sizes = extract_sizes_from_page(url)
#
# if sizes:
#     print(f"✅ Все размеры: {sizes}")
# else:
#     print("⛔ Не удалось извлечь размеры.")

import csv
import json
import os
import random
import re
import string
import uuid
from urllib.parse import urlparse

import django
import requests
from django.core.files.base import ContentFile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goabay_bot.settings")
django.setup()

from bs4 import BeautifulSoup
from django.utils.text import slugify
from decimal import Decimal

from bot_app.models import Product, ProductImage, ProductVariant, VariantImage
from site_app.models import Category, Brand




def generate_random_id(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def extract_product_info_and_variations(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.ID, 'pdp-product-title')))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Основная информация о товаре
        brand = 'Puma'
        print('Brand: ', brand)
        product_name_tag = soup.find('h1', id='pdp-product-title')
        product_name = product_name_tag.get_text(strip=True) if product_name_tag else "Неизвестное название"

        # Поиск цены со скидкой (sale price)
        sale_price = None

        # 1. Сначала ищем по data-test-id="item-sale-price-pdp" (скидочная цена)
        sale_price_tag = soup.find('span', {'data-test-id': 'price'})
        if sale_price_tag:
            sale_price = sale_price_tag.get_text(strip=True)

        # 2. Если не найдено, ищем обычную цену по data-test-id="item-price-pdp"
        if not sale_price:
            price_tag = soup.find('span', {'data-test-id': 'item-price-pdp'})
            if price_tag:
                sale_price = price_tag.get_text(strip=True)

        # 3. Если всё равно не найдено, ищем по классу font-bold (или его части)
        if not sale_price:
            price_tag = soup.find('span', class_=lambda x: x and 'font-bold' in x)
            if price_tag:
                sale_price = price_tag.get_text(strip=True)

        # 4. Если всё равно не найдено, ищем внутри блока с data-test-id="pdp-price-region"
        if not sale_price:
            price_region = soup.find('div', {'data-test-id': 'pdp-price-region'})
            if price_region:
                # Ищем любой span с числом и знаком валюты внутри price_region
                price_tag = price_region.find('span', string=lambda s: s and '₹' in s)
                if price_tag:
                    sale_price = price_tag.get_text(strip=True)
                else:
                    # Если и так не найдено, ищем любой span с цифрами внутри price_region
                    for span in price_region.find_all('span'):
                        txt = span.get_text(strip=True)
                        if any(char.isdigit() for char in txt):
                            sale_price = txt
                            break

        # sale_price теперь либо строка с ценой, либо None

        original_price_tag = soup.find('span', {'data-test-id': 'item-price-pdp'})
        original_price = original_price_tag.get_text(strip=True) if original_price_tag else None

        desc_block = soup.find('div', {'data-test-id': 'pdp-product-description'})
        description = ""
        if desc_block:
            text_div = desc_block.find('div', {'data-uds-child': 'text'})
            if text_div:
                description = text_div.get_text(separator="\n", strip=True)
            else:
                description = desc_block.get_text(separator="\n", strip=True)

        main_category = ""
        subcategories = ""
        breadcrumb_nav = soup.find('nav', id='breadcrumb')
        if breadcrumb_nav:
            crumbs = breadcrumb_nav.select('ul[data-uds-child="breadcrumb-list"] li a')
            categories = [crumb.get_text(strip=True) for crumb in crumbs]
            if categories and categories[0].lower() == 'home':
                categories = categories[1:]
            if categories:
                main_category = categories[0]
                if len(categories) > 1:
                    subcategories = " / ".join(categories[1:])

        wait.until(EC.presence_of_element_located((By.ID, 'style-picker')))
        color_variants = driver.find_elements(By.CSS_SELECTOR, '#style-picker label[data-test-id="color"]')

        product_random_id = generate_random_id()

        variations = []

        for idx, color_variant in enumerate(color_variants):
            try:
                color_name = color_variant.find_element(By.CSS_SELECTOR, 'span.sr-only').text.strip()
                if not color_name:
                    color_name = f"color_{idx+1}"

                driver.execute_script("arguments[0].scrollIntoView(true);", color_variant)
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'#style-picker label[data-test-id="color"]:nth-child({idx+1})')))
                try:
                    color_variant.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", color_variant)

                time.sleep(2)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'label[data-size] span[data-content="size-value"]')))

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                size_elements = soup.select('label[data-size] span[data-content="size-value"]')
                sizes = [size.get_text(strip=True) for size in size_elements if size.get_text(strip=True)]
                if not sizes:
                    sizes = ['Нет в наличии']

                gallery_section = soup.find('section', {'data-test-id': 'product-image-gallery-section'})
                main_image = None
                all_images = []
                if gallery_section:
                    main_img_tag = gallery_section.find('img', {'data-test-id': 'pdp-main-image'})
                    if main_img_tag and main_img_tag.has_attr('src'):
                        main_image = main_img_tag['src']
                    for img_tag in gallery_section.find_all('img'):
                        if img_tag.has_attr('src'):
                            all_images.append(img_tag['src'])
                    all_images = list(dict.fromkeys(all_images))

                variation = {
                    'color': color_name,
                    'sizes': sizes,
                    'main_image': main_image,
                    'all_images': all_images
                }

                variations.append(variation)

            except Exception as e:
                print(f"❌ Ошибка при обработке цвета '{color_name}': {e}")

        product_info = {
            'brand': brand,
            'random_id': product_random_id,
            'product_url': url,
            'product_name': product_name,
            'main_category': main_category,
            'subcategories': subcategories,
            'sale_price': sale_price,
            'original_price': original_price,
            'description': description.replace("\n", " ").strip(),
            'product_type': 'variative' if len(variations) > 1 else 'simple',
            'variations': variations
        }

        return [product_info]  # Возвращаем список с одним элементом — основным продуктом

    except Exception as e:
        print(f"❌ Ошибка при загрузке страницы или поиске элементов: {e}")
    finally:
        driver.quit()

    return []


# Функции сохранения

def variations_to_str(variations):
    """
    Преобразует список вариаций в строку для CSV:
    color|size1,size2|main_image|img1,img2; color2|...
    """
    result = []
    for var in variations:
        color = var.get('color', '')
        sizes = ",".join(var.get('sizes', []))
        main_image = var.get('main_image', '')
        all_images = ",".join(var.get('all_images', []))
        result.append(f"{color}|{sizes}|{main_image}|{all_images}")
    return " | ".join(result)


# def variations_to_str(variations):
#     """
#     Преобразует список вариаций в строку для CSV.
#     Каждая вариация — набор ключ:значение, размеры перечислены через запятую.
#     Вариации разделены ' | '.
#     """
#     if not variations:
#         return ''
#
#     parts = []
#     for var in variations:
#         color = var.get('color', '')
#         price = var.get('price', '')
#         main_image = var.get('main_image', '')
#         sizes = var.get('sizes', [])
#         sizes_str = ','.join(sizes) if sizes else ''
#
#         # Формируем строку вариации
#         var_str = f"color:{color}; price:{price}; sizes:[{sizes_str}]; image:{main_image}"
#         parts.append(var_str)
#
#     return ' | '.join(parts)


def save_to_csv(products, filename='puma-products.csv'):
    """
        Сохраняет список товаров и их вариаций в csv-формате, совместимом с WooCommerce.
    """
    # Собираем все возможные размеры и цвета для создания колонок
    all_colors = set()
    all_sizes = set()
    for product in products:
        for var in product.get('variations', []):
            all_colors.add(var.get('color', ''))
            all_sizes.update(var.get('sizes', []))

    # WooCommerce-совместимые поля + ваши
    fieldnames = [
        'ID', 'Type', 'SKU', 'Name', 'Parent', 'Brand', 'Product URL', 'Main Category', 'Subcategories',
        'Sale Price', 'Original Price', 'Description', 'Main Image', 'All Images',
        'attribute:Color', 'attribute:Size'
    ]

    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for product in products:
            # Основной товар (variable)
            parent_id = product['random_id']
            writer.writerow({
                'ID': parent_id,
                'Type': 'variable',
                'SKU': parent_id,
                'Name': product['product_name'],
                'Parent': '',
                'Brand': product['brand'],
                'Product URL': product['product_url'],
                'Main Category': product['main_category'],
                'Subcategories': product['subcategories'],
                'Sale Price': product['sale_price'],
                'Original Price': product['original_price'],
                'Description': product['description'],
                'Main Image': '',
                'All Images': '',
                'attribute:Color': ', '.join(sorted(all_colors)),
                'attribute:Size': ', '.join(sorted(all_sizes)),
            })

            # Вариации
            for var in product.get('variations', []):
                for size in var.get('sizes', []):
                    writer.writerow({
                        'ID': '',
                        'Type': 'variation',
                        'SKU': f"{parent_id}-{var.get('color', '')}-{size}",
                        'Name': '',
                        'Parent': parent_id,
                        'Brand': '',
                        'Product URL': product['product_url'],
                        'Main Category': '',
                        'Subcategories': '',
                        'Sale Price': product['sale_price'],
                        'Original Price': product['original_price'],
                        'Description': '',  # Обычно описание только у основного товара
                        'Main Image': var.get('main_image', ''),
                        'All Images': ','.join(var.get('all_images', [])),
                        'attribute:Color': var.get('color', ''),
                        'attribute:Size': size,
                    })

    print(f"CSV для WooCommerce успешно сохранён: {filename}")


def save_to_json(data, filename='products.json'):
    if not data:
        print("Нет данных для сохранения.")
        return
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4, ensure_ascii=False)
    print(f"Данные успешно сохранены в файл {filename}")

def get_or_create_brand(brand_name):
    slug = slugify(brand_name)
    brand = Brand.objects.filter(slug=slug).first()
    if brand is None:
        brand = Brand.objects.create(name=brand_name, slug=slug)
    return brand

def get_or_create_category(name, parent=None):
    category = Category.objects.filter(name=name, parent=parent).first()
    if category is None:
        category = Category.objects.create(name=name, parent=parent)
    return category

# def save_image_from_url(instance, image_field_name, image_url):
#     try:
#         response = requests.get(image_url)
#         response.raise_for_status()
#         img_data = response.content
#         filename = image_url.split("/")[-1].split("?")[0]  # Убираем параметры из URL
#         getattr(instance, image_field_name).save(filename, ContentFile(img_data), save=True)
#         print(f"Изображение сохранено: {filename}")
#     except Exception as e:
#         print(f"Ошибка при сохранении изображения {image_url}: {e}")



MAX_LENGTH = 100  # Максимальная длина для CharField, при необходимости меняйте

def truncate_str(s, max_len=MAX_LENGTH):
    if not s:
        return ''
    return s[:max_len] if len(s) > max_len else s



def save_image_from_url(instance, field_name, url):
    try:
        if not url:
            return
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        file_name = os.path.basename(url.split("?")[0])
        getattr(instance, field_name).save(file_name, ContentFile(response.content), save=True)
        print(f"📸 Изображение сохранено: {file_name}")
    except Exception as e:
        print(f"❌ Ошибка при загрузке изображения {url}: {e}")

# def save_parsed_product_to_db(parsed_product, brand_name='Puma'):
#     print("\n🔧 Начинаем сохранение товара...")
#
#     # 1. Категории
#     parent = None
#     main_category = parsed_product.get('main_category', '')
#     subcategories = parsed_product.get('subcategories', '')
#
#     # Собираем список категорий
#     cats = []
#     if main_category and main_category.strip():
#         cats.append(main_category.strip())
#
#     if subcategories and subcategories.strip():
#         cats.extend([c.strip() for c in subcategories.split('/') if c.strip()])
#
#     # === ДОПОЛНИТЕЛЬНЫЙ ПОИСК КАТЕГОРИЙ В HTML ===
#     if not cats and 'html' in parsed_product:
#         soup = BeautifulSoup(parsed_product['html'], 'html.parser')
#         # Ищем все li с классом, содержащим 'breadcrumb-list-item'
#         breadcrumb_items = soup.find_all('li', class_=lambda x: x and 'breadcrumb-list-item' in x)
#         for item in breadcrumb_items:
#             # Ищем <a> внутри <li>
#             a = item.find('a')
#             if a:
#                 cat = a.get_text(strip=True)
#                 if cat:
#                     cats.append(cat)
#     # === КОНЕЦ ДОПОЛНИТЕЛЬНОГО ПОИСКА ===
#
#     if not cats:
#         # Если категорий нет, используем дефолтную
#         cats = ['Uncategorized']
#         print(
#             f"⚠️ Для товара '{parsed_product.get('product_name', 'Без имени')}' не найдены категории, сохранено в 'Uncategorized'")
#
#     main_cat, *subcats = cats
#
#     for cat_name in [main_cat] + subcats:
#         parent, _ = Category.objects.get_or_create(name=cat_name, parent=parent)
#     category = parent
#     print(f"📂 Категория: {category.name}")
#
#     # 2. Бренд
#     brand_slug = slugify(brand_name)
#     brand = Brand.objects.filter(slug=brand_slug).first()
#     if not brand:
#         brand = Brand.objects.create(name=brand_name, slug=brand_slug)
#         print(f"🆕 Создан новый бренд: {brand_name}")
#     else:
#         print(f"🔄 Найден бренд: {brand_name}")
#
#     # 3. Продукт
#     base_slug = slugify(parsed_product['product_name'])
#     product_slug = f"{base_slug}"[:500]
#     print(f"🆔 Slug продукта: {product_slug}")
#
#     try:
#         product = Product.objects.get(slug=product_slug)
#         print("🔄 Продукт найден, обновляем данные...")
#
#         updated = False
#         if product.name != parsed_product['product_name']:
#             product.name = parsed_product['product_name']
#             updated = True
#         if product.desc != parsed_product.get('description', ''):
#             product.desc = parsed_product.get('description', '')
#             updated = True
#         if product.brand != brand:
#             product.brand = brand
#             updated = True
#         try:
#             new_price = Decimal(str(parsed_product.get('sale_price', '')).replace('₹', '').replace(',',
#                                                                                                    '').strip()) if parsed_product.get(
#                 'sale_price') else None
#             if product.price != new_price:
#                 product.price = new_price
#                 updated = True
#         except:
#             pass
#         try:
#             new_discount = Decimal(str(parsed_product.get('original_price', '')).replace('₹', '').replace(',',
#                                                                                                           '').strip()) if parsed_product.get(
#                 'original_price') else None
#             if product.discount != new_discount:
#                 product.discount = new_discount
#                 updated = True
#         except:
#             pass
#         if updated:
#             product.save()
#             print("🔄 Продукт обновлён")
#
#     except Product.DoesNotExist:
#         print("🆕 Продукт не найден, создаём новый...")
#         product = Product.objects.create(
#             slug=product_slug,
#             name=parsed_product['product_name'],
#             desc=parsed_product.get('description', ''),
#             brand=brand,
#             price=None,
#             discount=None
#         )
#         print("✅ Продукт создан")
#
#     # Категория
#     if not product.category.filter(id=category.id).exists():
#         product.category.add(category)
#         print(f"📁 Категория добавлена: {category.name}")
#
#     # Главное изображение продукта (берём из первой вариации, если нет)
#     main_img_url = parsed_product.get('variations', [{}])[0].get('main_image')
#     if main_img_url and (not product.image or not product.image.name):
#         save_image_from_url(product, 'image', main_img_url)
#
#     # Собираем все фото вариаций для добавления в дополнительные фото продукта
#     all_variant_images = set()
#     for var in parsed_product.get('variations', []):
#         main_img = var.get('main_image')
#         if main_img:
#             all_variant_images.add(main_img)
#
#     # Добавляем дополнительные фото продукта (включая фото вариаций)
#     all_images = {img for var in parsed_product.get('variations', []) for img in var.get('all_images', [])}
#     all_images.update(all_variant_images)  # объединяем с фото вариаций
#
#     for img_url in all_images:
#         if img_url:
#             # Проверяем, есть ли уже такое изображение у продукта
#             exists = ProductImage.objects.filter(product=product, image=img_url).exists()
#             if not exists:
#                 img_instance = ProductImage(product=product)
#                 save_image_from_url(img_instance, 'image', img_url)
#                 img_instance.save()
#
#     # Вариации — один объект на цвет с списком размеров
#     for var in parsed_product.get('variations', []):
#         color = (var.get('color') or '').strip()[:255]
#         sizes = var.get('sizes', []) or ['']  # если пусто, создаём вариацию без размера
#         main_image_url = var.get('main_image')
#         try:
#             price_var = Decimal(str(var.get('price')).replace('₹', '').replace(',', '').strip()) if var.get('price') else product.price
#         except:
#             price_var = product.price
#         desc_var = var.get('description', '') or parsed_product.get('description', '')
#
#         sku = f"{product_slug}-{color.replace(' ', '').replace('/', '')}"[:100]
#
#         variant_obj, created = ProductVariant.objects.get_or_create(
#             product=product,
#             color=color,
#             defaults={
#                 'size': sizes,
#                 'sku': sku,
#                 'price': price_var,
#             }
#         )
#         if not created:
#             updated = False
#             # Обновляем размеры, если изменились
#             if set(variant_obj.size) != set(sizes):
#                 variant_obj.sizes = sizes
#                 updated = True
#             if variant_obj.price != price_var:
#                 variant_obj.price = price_var
#                 updated = True
#             if variant_obj.description != desc_var:
#                 variant_obj.description = desc_var
#                 updated = True
#             if updated:
#                 variant_obj.save()
#                 print(f"🔄 Вариация обновлена: color={color}")
#
#         # Главное фото вариации
#         if main_image_url and (not variant_obj.image or not variant_obj.image.name):
#             save_image_from_url(variant_obj, 'image', main_image_url)
#
#         # Дополнительные фото вариации
#         for img_url in var.get('all_images', []):
#             if img_url and not variant_obj.additional_images.filter(image=img_url).exists():
#                 img_instance = VariantImage(variant=variant_obj)
#                 save_image_from_url(img_instance, 'image', img_url)
#                 img_instance.save()
#
#         print(f"{'✅' if created else '🔄'} Вариация: color={color}, sizes={sizes}, sku={sku}")
#
#     print(f"\n✅ Продукт сохранён: {product.name}\n")

def save_parsed_product_to_db(parsed_product, brand_name='Puma'):
    print("\n🔧 Начинаем сохранение товара...")

    # 1. Категории
    parent = None
    main_category = parsed_product.get('main_category', '')
    subcategories = parsed_product.get('subcategories', '')

    # Собираем список категорий
    cats = []
    if main_category and main_category.strip():
        cats.append(main_category.strip())

    if subcategories and subcategories.strip():
        cats.extend([c.strip() for c in subcategories.split('/') if c.strip()])

    # === ДОПОЛНИТЕЛЬНЫЙ ПОИСК КАТЕГОРИЙ В HTML ===
    if not cats and 'html' in parsed_product:
        soup = BeautifulSoup(parsed_product['html'], 'html.parser')
        # Ищем все li с классом, содержащим 'breadcrumb-list-item'
        breadcrumb_items = soup.find_all('li', class_=lambda x: x and 'breadcrumb-list-item' in x)
        for item in breadcrumb_items:
            # Ищем <a> внутри <li>
            a = item.find('a')
            if a:
                cat = a.get_text(strip=True)
                if cat:
                    cats.append(cat)
    # === КОНЕЦ ДОПОЛНИТЕЛЬНОГО ПОИСКА ===

    if not cats:
        # Если категорий нет, используем дефолтную
        cats = ['Uncategorized']
        print(
            f"⚠️ Для товара '{parsed_product.get('product_name', 'Без имени')}' не найдены категории, сохранено в 'Uncategorized'")

    main_cat, *subcats = cats

    for cat_name in [main_cat] + subcats:
        parent, _ = Category.objects.get_or_create(name=cat_name, parent=parent)
    category = parent
    print(f"📂 Категория: {category.name}")

    # 2. Бренд
    brand_slug = slugify(brand_name)
    brand = Brand.objects.filter(slug=brand_slug).first()
    if not brand:
        brand = Brand.objects.create(name=brand_name, slug=brand_slug)
        print(f"🆕 Создан новый бренд: {brand_name}")
    else:
        print(f"🔄 Найден бренд: {brand_name}")

    # 3. Продукт
    base_slug = slugify(parsed_product['product_name'])
    product_slug = f"{base_slug}"[:500]
    print(f"🆔 Slug продукта: {product_slug}")

    try:
        product = Product.objects.get(slug=product_slug)
        print("🔄 Продукт найден, обновляем данные...")

        updated = False
        if product.name != parsed_product['product_name']:
            product.name = parsed_product['product_name']
            updated = True
        if product.desc != parsed_product.get('description', ''):
            product.desc = parsed_product.get('description', '')
            updated = True
        if product.brand != brand:
            product.brand = brand
            updated = True
        try:
            new_price = Decimal(str(parsed_product.get('sale_price', '')).replace('₹', '').replace(',',
                                                                                                   '').strip()) if parsed_product.get(
                'sale_price') else None
            if product.price != new_price:
                product.price = new_price
                updated = True
        except:
            pass
        try:
            new_discount = Decimal(str(parsed_product.get('original_price', '')).replace('₹', '').replace(',',
                                                                                                          '').strip()) if parsed_product.get(
                'original_price') else None
            if product.discount != new_discount:
                product.discount = new_discount
                updated = True
        except:
            pass
        if updated:
            product.save()
            print("🔄 Продукт обновлён")

    except Product.DoesNotExist:
        print("🆕 Продукт не найден, создаём новый...")
        product = Product.objects.create(
            slug=product_slug,
            name=parsed_product['product_name'],
            desc=parsed_product.get('description', ''),
            brand=brand,
            price=None,
            discount=None
        )
        print("✅ Продукт создан")

    # Категория
    if not product.category.filter(id=category.id).exists():
        product.category.add(category)
        print(f"📁 Категория добавлена: {category.name}")

    # Главное изображение продукта (берём из первой вариации, если нет)
    main_img_url = parsed_product.get('variations', [{}])[0].get('main_image')
    if main_img_url and (not product.image or not product.image.name):
        save_image_from_url(product, 'image', main_img_url)

    # Собираем все фото вариаций для добавления в дополнительные фото продукта
    all_variant_images = set()
    for var in parsed_product.get('variations', []):
        main_img = var.get('main_image')
        if main_img:
            all_variant_images.add(main_img)

    # Добавляем дополнительные фото продукта (включая фото вариаций)
    all_images = {img for var in parsed_product.get('variations', []) for img in var.get('all_images', [])}
    all_images.update(all_variant_images)  # объединяем с фото вариаций

    for img_url in all_images:
        if img_url:
            # Проверяем, есть ли уже такое изображение у продукта
            exists = ProductImage.objects.filter(product=product, image=img_url).exists()
            if not exists:
                img_instance = ProductImage(product=product)
                save_image_from_url(img_instance, 'image', img_url)
                img_instance.save()

    # Вариации — один объект на цвет с списком размеров
    for var in parsed_product.get('variations', []):
        color = (var.get('color') or '').strip()[:255]
        sizes = var.get('sizes', []) or ['']  # если пусто, создаём вариацию без размера
        main_image_url = var.get('main_image')
        try:
            price_var = Decimal(str(var.get('price')).replace('₹', '').replace(',', '').strip()) if var.get('price') else product.price
        except:
            price_var = product.price
        desc_var = var.get('description', '') or parsed_product.get('description', '')

        sku = f"{product_slug}-{color.replace(' ', '').replace('/', '')}"[:100]

        variant_obj, created = ProductVariant.objects.get_or_create(
            product=product,
            color=color,
            defaults={
                'size': sizes,
                'sku': sku,
                'price': price_var,
            }
        )
        if not created:
            updated = False
            # Обновляем размеры, если изменились
            if set(variant_obj.size) != set(sizes):
                variant_obj.sizes = sizes
                updated = True
            if variant_obj.price != price_var:
                variant_obj.price = price_var
                updated = True
            if variant_obj.description != desc_var:
                variant_obj.description = desc_var
                updated = True
            if updated:
                variant_obj.save()
                print(f"🔄 Вариация обновлена: color={color}")

        # Главное фото вариации
        if main_image_url and (not variant_obj.image or not variant_obj.image.name):
            save_image_from_url(variant_obj, 'image', main_image_url)

        # Дополнительные фото вариации
        for img_url in var.get('all_images', []):
            if img_url and not variant_obj.additional_images.filter(image=img_url).exists():
                img_instance = VariantImage(variant=variant_obj)
                save_image_from_url(img_instance, 'image', img_url)
                img_instance.save()

        print(f"{'✅' if created else '🔄'} Вариация: color={color}, sizes={sizes}, sku={sku}")

    print(f"\n✅ Продукт сохранён: {product.name}\n")


def collect_product_links_with_scroll(category_url, scroll_pause=2, max_scrolls=30):
    """
    Собирает все ссылки на продукты на странице категории с динамической подгрузкой (скроллом).
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)

    try:
        driver.get(category_url)
        last_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = 0

        while scrolls < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Достигли конца страницы
            last_height = new_height
            scrolls += 1

        # Теперь собираем ссылки из полностью загруженного HTML
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/in/en/pd/' in href:
                full_url = 'https://in.puma.com' + href if href.startswith('/') else href
                product_links.add(full_url)
        return list(product_links)
    finally:
        driver.quit()



# Пример основного запуска:
# if __name__ == "__main__":
#     url = "https://in.puma.com/in/en/pd/court-shatter-low-sneakers/399844?size=0200&swatch=04"
#     product_data = extract_product_info_and_variations(url)
#     save_to_csv(product_data)
#     save_to_json(product_data)
#     for product in product_data:
#         save_parsed_product_to_db(product)
if __name__ == "__main__":
    MAIN_CATEGORIES = [
        'https://in.puma.com/in/en/rcb-launch',
        # Добавьте другие категории, если нужно
    ]

    all_product_links = set()
    for cat_url in MAIN_CATEGORIES:
        links = collect_product_links_with_scroll(cat_url)
        all_product_links.update(links)
    print(f"Найдено {len(all_product_links)} товаров для парсинга.")

    all_products = []
    for url in all_product_links:
        print(f"Парсим: {url}")
        products = extract_product_info_and_variations(url)
        all_products.extend(products)  # ДОБАВЛЯЕМ результат, а не products.extend(products)

    print(f"Всего успешно спарсено товаров: {len(all_products)}")

    # Сохраняем результат
    save_to_csv(all_products)
    save_to_json(all_products)
    for product in all_products:
        save_parsed_product_to_db(product)
