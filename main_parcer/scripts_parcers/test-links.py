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

from main_parcer.scripts_parcers.categories import CATEGORIES

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goabay_bot.settings")
django.setup()

from bot_app.models import Product
from site_app.models import Category, Brand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


BASE_URL = "https://in.puma.com"

MAIN_CATEGORIES = [
    'https://in.puma.com/in/en/new-season',
    'https://in.puma.com/in/en/mens',
    'https://in.puma.com/in/en/womens',
    'https://in.puma.com/in/en/motorsport',
    'https://in.puma.com/in/en/kids',
    'https://in.puma.com/in/en/puma-sale-collection',
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
                except Exception:
                    continue

            if len(product_links) == last_links_count:
                break
            else:
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

    for script_tag in script_tags:
        try:
            json_data = json.loads(script_tag.string)
        except:
            continue

        typ = json_data.get('@type')
        if typ == 'ProductGroup':
            brand_name = json_data.get('brand', {}).get('name')
            for variant in json_data.get('hasVariant', []):
                products.append({
                    'name': variant.get('name'),
                    'url': variant.get('url') or json_data.get('url'),
                    'price': variant.get('offers', {}).get('price'),
                    'currency': variant.get('offers', {}).get('priceCurrency'),
                    'image': variant.get('image'),
                    'brand': brand_name,
                    'category': main_cat,
                    'subcategory': sub_cat,
                    'color': variant.get('color'),
                    'size': sizes_str,
                    'description': description,
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
    for item in products:
        if not item.get('name'):
            continue

        slug = slugify(item['name'])[:500]

        brand = None
        if item.get('brand'):
            brand_name = item['brand'].strip()
            brand_slug = slugify(brand_name)
            brand, _ = Brand.objects.get_or_create(name=brand_name, slug=brand_slug)

        category_path = find_category_path(item.get('category'), item.get('subcategory'))
        category_obj = get_or_create_category_from_path(category_path)

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

        if category_obj:
            product.category.set([category_obj])

        product.save()


def save_json_and_csv(all_products):
    os.makedirs('jsons', exist_ok=True)
    all_data = []

    for url_key, products in all_products.items():
        parsed = urlparse(url_key).path.strip('/').split('/')
        main_cat = parsed[2] if len(parsed) > 2 else 'unknown'
        sub_cat = parsed[-1]

        for p in products:
            p['category'] = main_cat
            p['subcategory'] = sub_cat
            all_data.append(p)

        file_prefix = f"{main_cat}__{sub_cat}".replace("/", "_")
        with open(f"jsons/{file_prefix}.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'url', 'price', 'currency', 'image', 'brand', 'category', 'subcategory', 'color', 'size', 'description'])
            writer.writeheader()
            for product in products:
                product['image'] = product['image'][0] if isinstance(product['image'], list) else product['image']
                writer.writerow(product)

    with open('jsons/product_puma_all.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    all_products_by_category = {}

    for category_url in MAIN_CATEGORIES:
        print(f"\n▶ Обрабатываем подкатегорию: {category_url}")
        product_urls = collect_product_links_from_category(category_url)
        print(f"  ➤ Найдено {len(product_urls)} товаров.")

        parsed = urlparse(category_url).path.strip('/').split('/')
        main_cat = parsed[2] if len(parsed) > 2 else 'unknown'
        sub_cat = parsed[-1]

        products = []
        for url in product_urls:
            try:
                response = requests.get(url, timeout=20)
                response.raise_for_status()
                products.extend(parse_json_ld(response.text, main_cat, sub_cat))
                print(f"✅ Спарсен продукт: {url}")
            except Exception as e:
                print(f"❌ Ошибка: {url} — {e}")
        all_products_by_category[category_url] = products

    save_json_and_csv(all_products_by_category)

    all_flat = []
    for prods in all_products_by_category.values():
        all_flat.extend(prods)
    save_to_db(all_flat)

    print(f"\n✅ Парсинг завершён. Всего товаров: {len(all_flat)}")
