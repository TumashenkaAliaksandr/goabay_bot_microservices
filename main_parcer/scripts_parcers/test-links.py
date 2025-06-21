# Объединённый и доработанный парсер Puma с поддержкой множественных категорий, правильной иерархией, учётом вариаций товаров,
# сохранением JSON и CSV, а также записью в Django базу данных с Category и Brand.

import os
import json
import csv
import time
import django
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from django.utils.text import slugify
from django.core.files.base import ContentFile

# Django init
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goabay_bot.settings")
django.setup()

from bot_app.models import Product
from site_app.models import Category, Brand

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


BASE_URL = "https://in.puma.com"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

MAIN_CATEGORIES = [
    'https://in.puma.com/in/en/new-season',
    'https://in.puma.com/in/en/mens',
    'https://in.puma.com/in/en/womens',
    'https://in.puma.com/in/en/sports',
    'https://in.puma.com/in/en/motorsport',
    'https://in.puma.com/in/en/lifestyle',
    'https://in.puma.com/in/en/kids',
    'https://in.puma.com/in/en/puma-sale-collection',
    'https://in.puma.com/in/en/rcb-launch',
]


def get_category_links(main_url):
    try:
        response = requests.get(main_url, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка при загрузке {main_url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/in/en') and '/pd/' not in href and '?' not in href:
            full_url = BASE_URL + href
            links.add(full_url)
    return list(links)


def collect_product_links_from_category(category_url, scroll_pause=2, max_scrolls=100):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)

    print(f"Загружаем категорию: {category_url}")
    try:
        driver.get(category_url)
    except Exception as e:
        print(f"❌ Ошибка загрузки страницы {category_url}: {e}")
        driver.quit()
        return []

    if "Page Not Found" in driver.page_source or "404" in driver.title:
        print(f"⚠️ Страница не найдена: {category_url}")
        driver.quit()
        return []

    product_links = set()
    scrolls = 0
    last_height = driver.execute_script("return document.body.scrollHeight")

    while scrolls < max_scrolls:
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(scroll_pause)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scrolls += 1
        except Exception as e:
            print(f"⚠️ Ошибка при прокрутке: {e}")
            break

    script_tags = driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')
    for tag in script_tags:
        try:
            content = tag.get_attribute('innerHTML')
            if not content:
                continue
            data = json.loads(content)
            if data.get('@type') == 'ItemList':
                for item in data.get('itemListElement', []):
                    url = item.get('item', {}).get('url')
                    if url:
                        product_links.add(url)
        except Exception:
            continue

    driver.quit()
    return list(product_links)


def collect_all_product_links(main_urls):
    all_links = {}
    for main_url in main_urls:
        sub_links = get_category_links(main_url)
        for sub_url in sub_links:
            print(f"\n▶ Обрабатываем подкатегорию: {sub_url}")
            links = collect_product_links_from_category(sub_url)
            print(f"  ➤ Найдено {len(links)} товаров.")
            all_links[sub_url] = links
    return all_links


def parse_json_ld(html_content, main_cat, sub_cat):
    soup = BeautifulSoup(html_content, 'html.parser')
    script_tags = soup.find_all('script', type='application/ld+json')
    products = []
    brand_from_group = None
    group_url = None

    for script_tag in script_tags:
        try:
            content = script_tag.string
            if not content:
                continue
            json_data = json.loads(content)
        except Exception:
            continue

        typ = json_data.get('@type')

        if typ == 'ProductGroup':
            brand_from_group = json_data.get('brand', {}).get('name')
            group_url = json_data.get('url')
            for variant in json_data.get('hasVariant', []):
                products.append({
                    'name': variant.get('name'),
                    'url': variant.get('url') or group_url,
                    'price': variant.get('offers', {}).get('price'),
                    'currency': variant.get('offers', {}).get('priceCurrency'),
                    'image': variant.get('image'),
                    'brand': brand_from_group,
                    'category': main_cat,
                    'subcategory': sub_cat,
                    'color': variant.get('color'),
                    'size': '',
                    'description': '',
                })

        elif typ == 'Product':
            products.append({
                'name': json_data.get('name'),
                'url': json_data.get('url'),
                'price': json_data.get('offers', {}).get('price'),
                'currency': json_data.get('offers', {}).get('priceCurrency'),
                'image': json_data.get('image'),
                'brand': json_data.get('brand', {}).get('name'),
                'category': main_cat,
                'subcategory': sub_cat,
                'color': json_data.get('color'),
                'size': '',
                'description': '',
            })

    description_tag = soup.find('div', {'data-test-id': 'pdp-product-description'})
    description = description_tag.get_text(strip=True) if description_tag else "Описание не найдено"
    sizes = []
    for label in soup.select('label[data-size]'):
        size_span = label.select_one('span[data-content="size-value"]')
        if size_span:
            sizes.append(size_span.get_text(strip=True))
    sizes_str = ', '.join(sizes) if sizes else 'Нет в наличии'

    for product in products:
        product['description'] = description
        product['size'] = sizes_str

    return products


def save_to_db(products):
    for item in products:
        if not item.get('name'):
            continue

        slug = slugify(item['name'])[:500]
        brand = None
        if item.get('brand'):
            brand_name = item['brand'].strip()
            brand_slug = slugify(brand_name)
            brand, _ = Brand.objects.get_or_create(name=brand_name, slug=brand_slug)

        categories = []
        if item.get('category') and item.get('subcategory'):
            parent_cat, _ = Category.objects.get_or_create(name=item['category'].strip())
            subcat, _ = Category.objects.get_or_create(name=item['subcategory'].strip(), parent=parent_cat)
            categories.append(subcat)

        product, created = Product.objects.get_or_create(slug=slug, defaults={
            'name': item['name'],
            'brand': brand,
            'desc': item.get('description', ''),
            'price': item.get('price') or 0,
            'color': item.get('color', ''),
            'sizes': item.get('size', ''),
            'stock_status': 'in_stock',
        })

        if not created:
            product.price = item.get('price') or product.price
            product.desc = item.get('description') or product.desc
            product.color = item.get('color') or product.color
            product.sizes = item.get('size') or product.sizes

        if item.get('image') and (created or not product.image):
            try:
                img_url = item['image'] if isinstance(item['image'], str) else item['image'][0]
                img_content = requests.get(img_url).content
                image_field = ContentFile(img_content, name=img_url.split('/')[-1])
                product.image.save(image_field.name, image_field)
            except Exception as e:
                print(f"⚠️ Ошибка загрузки изображения: {e}")

        if categories:
            product.category.set(categories)

        product.save()


def save_json_and_csv(all_products):
    os.makedirs('jsons', exist_ok=True)
    all_data = []

    for subcat_key, products in all_products.items():
        if not products:
            continue

        parsed = urlparse(subcat_key).path.strip('/').split('/')
        main_cat = parsed[2] if len(parsed) > 2 else 'unknown'
        sub_cat = parsed[-1]

        for p in products:
            p['category'] = main_cat
            p['subcategory'] = sub_cat
            all_data.append(p)

        filename_base = f"{main_cat}__{sub_cat}".replace("/", "_")
        with open(f"jsons/{filename_base}.csv", 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'url', 'price', 'currency', 'image', 'brand', 'category', 'subcategory', 'color', 'size', 'description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for product in products:
                if isinstance(product['image'], list):
                    product['image'] = product['image'][0]
                writer.writerow(product)

    with open('jsons/product_puma_all.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    all_links_by_category = collect_all_product_links(MAIN_CATEGORIES)
    all_products_by_category = {}

    for category_url, product_urls in all_links_by_category.items():
        parsed = urlparse(category_url).path.strip('/').split('/')
        main_cat = parsed[2] if len(parsed) > 2 else 'unknown'
        sub_cat = parsed[-1]

        products_for_category = []
        for product_url in product_urls:
            try:
                response = requests.get(product_url, timeout=10)
                response.raise_for_status()
                products = parse_json_ld(response.text, main_cat, sub_cat)
                products_for_category.extend(products)
                print(f"✅ Спарсен продукт: {product_url}")
            except Exception as e:
                print(f"❌ Ошибка: {product_url} — {e}")
        all_products_by_category[category_url] = products_for_category

    save_json_and_csv(all_products_by_category)

    all_flat = []
    for prods in all_products_by_category.values():
        all_flat.extend(prods)
    save_to_db(all_flat)

    print(f"\n✅ Парсинг завершён. Всего товаров: {len(all_flat)}")
