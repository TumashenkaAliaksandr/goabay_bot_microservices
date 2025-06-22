# -*- coding: utf-8 -*-
import os
import json
import time
import django
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from django.utils.text import slugify
from django.core.files.base import ContentFile

from main_parcer.scripts_parcers.categories import CATEGORIES

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goabay_bot.settings")
django.setup()

from bot_app.models import Product, ProductVariant
from site_app.models import Category, Brand

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


BASE_URL = "https://in.puma.com"
MAIN_CATEGORIES = [
    'https://in.puma.com/in/en/rcb-launch',
]


def collect_product_links_from_category(category_url, scroll_pause=2, max_wait_scrolls=300):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(180)
    driver.set_script_timeout(180)

    try:
        driver.get(category_url)
    except Exception as e:
        print(f"❌ Ошибка загрузки страницы {category_url}: {e}")
        driver.quit()
        return []

    product_links = set()
    last_links_count = 0
    wait_counter = 0

    while wait_counter < max_wait_scrolls:
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(scroll_pause)

            script_tags = driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')
            for tag in script_tags:
                try:
                    content = tag.get_attribute('innerHTML')
                    data = json.loads(content)
                    if data.get('@type') == 'ItemList':
                        for item in data.get('itemListElement', []):
                            url = item.get('item', {}).get('url')
                            if url:
                                product_links.add(url)
                except:
                    continue

            if len(product_links) == last_links_count:
                break
            last_links_count = len(product_links)
            wait_counter += 1
        except Exception as e:
            print(f"⚠️ Ошибка при прокрутке: {e}")
            break

    driver.quit()
    return list(product_links)


def parse_json_ld(html_content, main_cat, sub_cat):
    soup = BeautifulSoup(html_content, 'html.parser')
    script_tags = soup.find_all('script', type='application/ld+json')
    description_tag = soup.find('div', {'data-test-id': 'pdp-product-description'})
    description = description_tag.get_text(strip=True) if description_tag else "Описание не найдено"
    sizes = [s.get_text(strip=True) for s in soup.select('label[data-size] span[data-content="size-value"]')]
    sizes_str = ', '.join(sizes) if sizes else 'Нет в наличии'

    products = []

    for tag in script_tags:
        try:
            data = json.loads(tag.string)
        except:
            continue

        if data.get('@type') == 'ProductGroup':
            brand = data.get('brand', {}).get('name')
            product_name = data.get('name')
            product_url = data.get('url')

            for var in data.get('hasVariant', []):
                products.append({
                    'base_name': product_name,
                    'variant_name': var.get('name'),
                    'url': var.get('url') or product_url,
                    'price': var.get('offers', {}).get('price'),
                    'currency': var.get('offers', {}).get('priceCurrency'),
                    'image': var.get('image'),
                    'brand': brand,
                    'category': main_cat,
                    'subcategory': sub_cat,
                    'color': var.get('color'),
                    'size': sizes_str,
                    'description': description,
                })

    return products


def find_category_path(main_cat, sub_cat):
    for top, subs in CATEGORIES.items():
        for mid, leafs in subs.items():
            for leaf in leafs:
                if leaf.lower() in sub_cat.lower():
                    return [top, mid, leaf]
            if sub_cat.lower() in mid.lower():
                return [top, mid]
        if sub_cat.lower() in top.lower():
            return [top]
    return [main_cat, sub_cat] if main_cat and sub_cat else [main_cat or sub_cat]


def get_or_create_category_from_path(path):
    parent = None
    for name in path:
        if not name:
            continue
        obj, _ = Category.objects.get_or_create(name=name, parent=parent)
        parent = obj
    return parent


def save_to_db(products):
    grouped = {}
    for item in products:
        key = slugify(item['base_name'])
        grouped.setdefault(key, []).append(item)

    for slug, variants in grouped.items():
        base = variants[0]

        brand = None
        if base.get('brand'):
            brand_slug = slugify(base['brand'])
            brand, _ = Brand.objects.get_or_create(name=base['brand'], slug=brand_slug)

        cat_path = find_category_path(base['category'], base['subcategory'])
        cat_obj = get_or_create_category_from_path(cat_path)

        # Обновляем или создаем товар
        product, created = Product.objects.get_or_create(slug=slug, defaults={
            'name': base['base_name'],
            'brand': brand,
            'desc': base.get('description', ''),
            'price': base.get('price') or 0,
            'color': base.get('color', ''),
            'sizes': base.get('size', ''),
            'stock_status': 'in_stock'
        })

        # Обновление товара, если он уже существует
        if not created:
            product.name = base['base_name']
            product.brand = brand
            product.desc = base.get('description', '')
            product.price = base.get('price') or 0
            product.color = base.get('color', '')
            product.sizes = base.get('size', '')
            product.stock_status = 'in_stock'
            product.save()

        if cat_obj:
            product.category.set([cat_obj])

        for var in variants:
            sku = slugify(var['variant_name'])[:100]

            # Проверяем существование вариации
            variant_obj, created = ProductVariant.objects.get_or_create(
                sku=sku,
                defaults={
                    'product': product,
                    'color': var.get('color'),
                    'size': var.get('size')[:50],
                    'price': var.get('price') or 0,
                    'quantity': 0,
                    'description': var.get('description', '')
                }
            )

            # Обновляем вариацию, если она уже существует
            if not created:
                variant_obj.color = var.get('color')
                variant_obj.size = var.get('size')[:50]
                variant_obj.price = var.get('price') or 0
                variant_obj.description = var.get('description', '')
                variant_obj.save()

            # Обновляем/создаём изображение
            image_url = var.get('image')
            if image_url:
                if isinstance(image_url, list):
                    image_url = image_url[0]
                try:
                    img_data = requests.get(image_url).content
                    variant_obj.image.save(image_url.split("/")[-1], ContentFile(img_data), save=True)
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки изображения вариации: {e}")

        print(f"✅ Сохранён продукт: {product.name}")


if __name__ == '__main__':
    all_products = []

    for category_url in MAIN_CATEGORIES:
        print(f"\n▶ Обработка категории: {category_url}")
        links = collect_product_links_from_category(category_url)
        print(f"  ➤ Найдено ссылок: {len(links)}")

        parsed = urlparse(category_url).path.strip('/').split('/')
        main_cat = parsed[2] if len(parsed) > 2 else 'unknown'
        sub_cat = parsed[-1]

        for url in links:
            try:
                r = requests.get(url, timeout=30)
                r.raise_for_status()
                products = parse_json_ld(r.text, main_cat, sub_cat)
                all_products.extend(products)
                print(f"  ➕ {url} ({len(products)} вариаций)")
            except Exception as e:
                print(f"❌ Ошибка парсинга {url}: {e}")

    save_to_db(all_products)
    print(f"\n✅ Парсинг завершён. Всего товаров: {len(all_products)}")
