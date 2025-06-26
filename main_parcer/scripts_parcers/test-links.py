# # -*- coding: utf-8 -*-
# import csv
# import logging
# import os
# import json
# import re
# import time
# import django
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urlparse
# from django.utils.text import slugify
# from django.core.files.base import ContentFile
#
# from main_parcer.scripts_parcers.categories import CATEGORIES
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goabay_bot.settings")
# django.setup()
#
# from bot_app.models import Product, ProductVariant, ProductImage
# from site_app.models import Category, Brand
#
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
#
# BASE_URL = "https://in.puma.com"
# MAIN_CATEGORIES = [
#     'https://in.puma.com/in/en/rcb-launch',
# ]
#
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
#
#
#
# def extract_sizes_with_selenium(url):
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#
#
#     driver = webdriver.Chrome(options=options)
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
#
# def collect_product_links_from_category(category_url, scroll_pause=2, max_wait_scrolls=300):
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#
#     driver = webdriver.Chrome(options=options)
#     driver.set_page_load_timeout(180)
#     driver.set_script_timeout(180)
#
#     try:
#         driver.get(category_url)
#     except Exception as e:
#         print(f"❌ Ошибка загрузки страницы {category_url}: {e}")
#         driver.quit()
#         return []
#
#     product_links = set()
#     last_links_count = 0
#     wait_counter = 0
#
#     while wait_counter < max_wait_scrolls:
#         try:
#             driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
#             time.sleep(scroll_pause)
#
#             script_tags = driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')
#             for tag in script_tags:
#                 try:
#                     content = tag.get_attribute('innerHTML')
#                     data = json.loads(content)
#                     if data.get('@type') == 'ItemList':
#                         for item in data.get('itemListElement', []):
#                             url = item.get('item', {}).get('url')
#                             if url:
#                                 product_links.add(url)
#                 except:
#                     continue
#
#             if len(product_links) == last_links_count:
#                 break
#             last_links_count = len(product_links)
#             wait_counter += 1
#         except Exception as e:
#             print(f"⚠️ Ошибка при прокрутке: {e}")
#             break
#
#     driver.quit()
#     return list(product_links)
#
#
# def extract_sizes_from_html(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     # Используем map для извлечения всех размеров
#     sizes = list(map(lambda x: x.get_text(strip=True), soup.find_all('span', {'data-content': 'size-value'})))
#
#     return sizes if sizes else ['Нет в наличии']
#
#
# def parse_json_ld(html_content, main_cat, sub_cat):
#     soup = BeautifulSoup(html_content, 'html.parser')
#
#     next_data_script = soup.find('script', id='__NEXT_DATA__')
#     if next_data_script:
#         try:
#             data = json.loads(next_data_script.string)
#             next_data_products = parse_next_data_json(data, soup, main_cat, sub_cat)
#             if next_data_products:
#                 return next_data_products
#         except Exception as e:
#             print(f"⚠️ Ошибка парсинга __NEXT_DATA__: {e}")
#
#     return parse_json_ld_fallback(soup, main_cat, sub_cat)
#
#
# def extract_variant_info_from_insider(html):
#     """
#     Ищет в html скрипт с window.insider_object.product и извлекает color и size.
#     Возвращает dict с ключами 'color' и 'size' или пустой dict, если не найдено.
#     """
#     pattern = re.compile(r'window\.insider_object\.product\s*=\s*({.*?});', re.DOTALL)
#     match = pattern.search(html)
#     if not match:
#         return {}
#
#     try:
#         product_json_str = match.group(1)
#         # Иногда в JSON могут быть одинарные кавычки или невалидные символы, но обычно это валидный JS-объект
#         # Для безопасности можно заменить одинарные кавычки на двойные, если нужно:
#         # product_json_str = product_json_str.replace("'", '"')
#         product_data = json.loads(product_json_str)
#         return {
#             'color': product_data.get('color'),
#             'size': product_data.get('size')
#         }
#     except Exception as e:
#         print(f"⚠️ Ошибка парсинга insider_object.product: {e}")
#         return {}
#
#
# def parse_next_data_json(data, soup, main_cat, sub_cat):
#     products = []
#     try:
#         product = data['props']['pageProps'].get('product', {})
#         variants = product.get('variants', [])
#         base_name = product.get("name")
#         description_tag = soup.find('div', {'data-test-id': 'pdp-product-description'})
#         description = description_tag.get_text(strip=True) if description_tag else product.get('description', '')
#         html = str(soup)
#
#         for variant in variants:
#             image = variant.get("image", {}).get("url") or None
#             price = variant.get("price", {}).get("value")
#             currency = variant.get("price", {}).get("currency")
#
#             variant_url = variant.get("url")
#             insider_info = {}
#             sizes_str = 'Нет в наличии'
#             variant_html = ''
#
#             try:
#                 if variant_url:
#                     full_url = BASE_URL + variant_url if variant_url.startswith('/') else variant_url
#                     variant_resp = requests.get(full_url, timeout=10)
#                     if variant_resp.status_code == 200:
#                         variant_html = variant_resp.text
#                         insider_info = extract_variant_info_from_insider(variant_html)
#                         sizes_list = extract_sizes_from_html(variant_html)
#                         sizes_str = ', '.join(sizes_list)
#                 else:
#                     fallback_url = product.get("url") or product.get("pdpUrl") or ""
#                     if fallback_url:
#                         if not fallback_url.startswith("http"):
#                             fallback_url = BASE_URL + fallback_url
#                         sizes_list = extract_sizes_with_selenium(fallback_url)
#                         sizes_str = ', '.join(sizes_list)
#             except Exception as e:
#                 print(f"⚠️ Ошибка получения размеров вариации: {e}")
#
#             color = variant.get("color") or insider_info.get('color')
#             size = sizes_str
#
#             products.append({
#                 "base_name": base_name,
#                 "variant_name": variant.get("name"),
#                 "url": BASE_URL + variant_url if variant_url else None,
#                 "price": price,
#                 "currency": currency,
#                 "image": image,
#                 "brand": product.get("brand", {}).get("name", "PUMA"),
#                 "category": main_cat,
#                 "subcategory": sub_cat,
#                 "color": color,
#                 "size": size,
#                 "description": description,
#                 "html": variant_html
#             })
#
#     except Exception as e:
#         print(f"⚠️ Ошибка разбора данных из __NEXT_DATA__: {e}")
#
#     return products
#
#
# def parse_json_ld_fallback(soup, main_cat, sub_cat):
#     script_tags = soup.find_all('script', type='application/ld+json')
#     description_tag = soup.find('div', {'data-test-id': 'pdp-product-description'})
#     description = description_tag.get_text(strip=True) if description_tag else "Описание не найдено"
#
#     products = []
#     for tag in script_tags:
#         try:
#             data = json.loads(tag.string)
#         except:
#             continue
#
#         if data.get('@type') == 'ProductGroup':
#             brand = data.get('brand', {}).get('name')
#             product_name = data.get('name')
#
#             for var in data.get('hasVariant', []):
#                 variant_url = BASE_URL + var.get('url', '') if var.get('url') else None
#                 sizes_str = 'Нет в наличии'
#                 html = ''
#
#                 if variant_url:
#                     try:
#                         resp = requests.get(variant_url, timeout=10)
#                         if resp.status_code == 200:
#                             html = resp.text
#                             sizes_str = extract_sizes_from_html(html)
#                     except:
#                         pass
#
#                 products.append({
#                     'base_name': product_name,
#                     'variant_name': var.get('name'),
#                     'url': variant_url,
#                     'price': var.get('offers', {}).get('price'),
#                     'currency': var.get('offers', {}).get('priceCurrency'),
#                     'image': var.get('image'),
#                     'brand': brand,
#                     'category': main_cat,
#                     'subcategory': sub_cat,
#                     'color': var.get('color'),
#                     'size': sizes_str,
#                     'description': description,
#                     'html': html
#                 })
#
#     return products
#
#
# def find_category_path(main_cat, sub_cat):
#     for top, subs in CATEGORIES.items():
#         for mid, leafs in subs.items():
#             for leaf in leafs:
#                 if leaf.lower() in sub_cat.lower():
#                     return [top, mid, leaf]
#             if sub_cat.lower() in mid.lower():
#                 return [top, mid]
#         if sub_cat.lower() in top.lower():
#             return [top]
#     return [main_cat, sub_cat] if main_cat and sub_cat else [main_cat or sub_cat]
#
#
# def get_or_create_category_from_path(path):
#     parent = None
#     for name in path:
#         if not name:
#             continue
#         obj, _ = Category.objects.get_or_create(name=name, parent=parent)
#         parent = obj
#     return parent
#
#
# def save_to_db(products):
#     grouped = {}
#     for item in products:
#         key = slugify(item['base_name'])
#         grouped.setdefault(key, []).append(item)
#
#     json_data = []
#     csv_rows = []
#
#     for slug, variants in grouped.items():
#         base = variants[0]
#
#         if base.get('html') and (not base.get('size') or base.get('size') == 'Нет в наличии'):
#             base['size'] = extract_sizes_from_html(base['html'])
#
#         brand = None
#         if base.get('brand'):
#             brand_slug = slugify(base['brand'])
#             brand, _ = Brand.objects.get_or_create(name=base['brand'], slug=brand_slug)
#
#         cat_path = find_category_path(base['category'], base['subcategory'])
#         cat_obj = get_or_create_category_from_path(cat_path)
#
#         product, created = Product.objects.get_or_create(slug=slug, defaults={
#             'name': base['base_name'],
#             'brand': brand,
#             'desc': base.get('description', ''),
#             'price': base.get('price') or 0,
#             'color': base.get('color', ''),
#             'sizes': base.get('size', ''),
#             'stock_status': 'in_stock'
#         })
#
#         if not created:
#             product.name = base['base_name']
#             product.brand = brand
#             product.desc = base.get('description', '')
#             product.price = base.get('price') or 0
#             product.color = base.get('color', '')
#             product.sizes = base.get('size', '')
#             product.stock_status = 'in_stock'
#             product.save()
#
#         if cat_obj:
#             product.category.set([cat_obj])
#
#         main_image_url = base.get('image')
#         if main_image_url:
#             if isinstance(main_image_url, list):
#                 main_image_url = main_image_url[0]
#             try:
#                 img_data = requests.get(main_image_url).content
#                 product.image.save(main_image_url.split("/")[-1], ContentFile(img_data), save=True)
#             except Exception as e:
#                 print(f"⚠️ Ошибка загрузки главного изображения: {e}")
#
#         for img_url in base.get('additional_images', []):
#             try:
#                 img_data = requests.get(img_url).content
#                 ProductImage.objects.create(
#                     product=product,
#                     image=ContentFile(img_data, name=img_url.split("/")[-1])
#                 )
#             except Exception as e:
#                 print(f"⚠️ Ошибка загрузки дополнительного изображения: {e}")
#
#         for var in variants:
#             if var.get('html') and (not var.get('size') or var.get('size') == 'Нет в наличии'):
#                 var['size'] = extract_sizes_from_html(var['html'])
#
#             sku = slugify(var['variant_name'])[:100]
#             variant_obj, created = ProductVariant.objects.get_or_create(
#                 sku=sku,
#                 defaults={
#                     'product': product,
#                     'color': var.get('color'),
#                     'size': var.get('size')[:50],
#                     'price': var.get('price') or 0,
#                     'quantity': 0,
#                     'description': var.get('description', '')
#                 }
#             )
#
#             if not created:
#                 variant_obj.color = var.get('color')
#                 variant_obj.size = var.get('size')[:50]
#                 variant_obj.price = var.get('price') or 0
#                 variant_obj.description = var.get('description', '')
#                 variant_obj.save()
#
#             image_url = var.get('image')
#             if image_url:
#                 if isinstance(image_url, list):
#                     image_url = image_url[0]
#                 try:
#                     img_data = requests.get(image_url).content
#                     variant_obj.image.save(image_url.split("/")[-1], ContentFile(img_data), save=True)
#                 except Exception as e:
#                     print(f"⚠️ Ошибка загрузки изображения вариации: {e}")
#
#             csv_rows.append({
#                 'product_name': product.name,
#                 'brand': brand.name if brand else '',
#                 'price': var.get('price') or 0,
#                 'category': cat_obj.name if cat_obj else '',
#                 'color': var.get('color'),
#                 'size': var.get('size'),
#                 'sku': sku,
#                 'description': var.get('description', ''),
#                 'image': image_url
#             })
#
#         json_data.append({
#             'name': product.name,
#             'slug': product.slug,
#             'brand': brand.name if brand else '',
#             'desc': product.desc,
#             'price': product.price,
#             'color': product.color,
#             'sizes': product.sizes,
#             'image': main_image_url,
#             'category': cat_path,
#             'variants': variants
#         })
#
#         print(f"✅ Сохранён продукт: {product.name}")
#
#     os.makedirs('jsons', exist_ok=True)
#
#     with open('jsons/products_data.json', 'w', encoding='utf-8') as jf:
#         json.dump(json_data, jf, ensure_ascii=False, indent=4)
#
#     with open('jsons/products_data.csv', 'w', newline='', encoding='utf-8') as cf:
#         fieldnames = ['product_name', 'brand', 'price', 'category', 'color', 'size', 'sku', 'description', 'image']
#         writer = csv.DictWriter(cf, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(csv_rows)
#
#     print("📦 Данные успешно сохранены в JSON и CSV")
#
#
# if __name__ == '__main__':
#     all_products = []
#
#     for category_url in MAIN_CATEGORIES:
#         print(f"\n▶ Обработка категории: {category_url}")
#         links = collect_product_links_from_category(category_url)
#         print(f"  ➤ Найдено ссылок: {len(links)}")
#
#         parsed = urlparse(category_url).path.strip('/').split('/')
#         main_cat = parsed[2] if len(parsed) > 2 else 'unknown'
#         sub_cat = parsed[-1]
#
#         for url in links:
#             try:
#                 r = requests.get(url, timeout=30)
#                 r.raise_for_status()
#                 products = parse_json_ld(r.text, main_cat, sub_cat)
#                 all_products.extend(products)
#                 print(f"  ➕ {url} ({len(products)} вариаций)")
#             except Exception as e:
#                 print(f"❌ Ошибка парсинга {url}: {e}")
#
#     save_to_db(all_products)
#     print(f"\n✅ Парсинг завершён. Всего товаров: {len(all_products)}")
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

        sale_price_tag = soup.find('span', {'data-test-id': 'item-sale-price-pdp'})
        sale_price = sale_price_tag.get_text(strip=True) if sale_price_tag else None

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

def save_parsed_product_to_db(parsed_product, brand_name='Puma'):
    print("\n🔧 Начинаем сохранение товара...")

    # 1. Категории
    parent = None
    main_cat, *subcats = [c.strip() for c in ([parsed_product.get('main_category')] + parsed_product.get('subcategories', '').split('/')) if c.strip()]
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
            if set(variant_obj.sizes) != set(sizes):
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


def collect_product_links_from_category(category_url):
    """
    Собирает все ссылки на продукты на странице категории.
    """
    response = requests.get(category_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    product_links = set()
    # Ищем все <a> с нужным паттерном
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/in/en/pd/' in href:
            full_url = 'https://in.puma.com' + href if href.startswith('/') else href
            product_links.add(full_url)
    return list(product_links)



# Пример основного запуска:
if __name__ == "__main__":
    url = "https://in.puma.com/in/en/pd/court-shatter-low-sneakers/399844?size=0200&swatch=04"
    product_data = extract_product_info_and_variations(url)
    save_to_csv(product_data)
    save_to_json(product_data)
    for product in product_data:
        save_parsed_product_to_db(product)
# if __name__ == "__main__":
#     MAIN_CATEGORIES = [
#         'https://in.puma.com/in/en/rcb-launch',
#         # Добавьте другие категории, если нужно
#     ]
#
#     all_product_links = set()
#     for cat_url in MAIN_CATEGORIES:
#         links = collect_product_links_from_category(cat_url)
#         all_product_links.update(links)
#     print(f"Найдено {len(all_product_links)} товаров для парсинга.")
#
#     all_products = []
#     for url in all_product_links:
#         print(f"Парсим: {url}")
#         products = extract_product_info_and_variations(url)
#         all_products.extend(products)  # ДОБАВЛЯЕМ результат, а не products.extend(products)
#
#     print(f"Всего успешно спарсено товаров: {len(all_products)}")
#
#     # Сохраняем результат
#     save_to_csv(all_products)
#     save_to_json(all_products)
#     for product in all_products:
#         save_parsed_product_to_db(product)
