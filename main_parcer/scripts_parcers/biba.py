import os
import django
import csv
import requests
from bs4 import BeautifulSoup
import time
import json
import concurrent.futures
import logging
import random
import re
import urllib.request
from django.core.files import File
from io import BytesIO

# Инициализация Django (замените goabay_bot.settings на ваш settings)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goabay_bot.settings')
django.setup()

from bot_app.models import Product, ProductVariant
from site_app.models import Brand  # замените на ваши реальные приложения

logger = logging.getLogger('product_parser')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('parsing.log', mode='w', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0 Safari/537.36"
}

def slugify(text):
    slug = re.sub(r'[^\w\s-]', '', text or '').strip().lower()
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug or 'default-slug'

def ensure_dir_exists(filepath):
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def parse_json_ld(html):
    soup = BeautifulSoup(html, 'html.parser')
    product_json = None
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and data.get('@type') == 'Product':
                product_json = data
                break
            elif isinstance(data, list):
                for entry in data:
                    if entry.get('@type') == 'Product':
                        product_json = entry
                        break
        except (json.JSONDecodeError, TypeError):
            continue
    return product_json

def parse_product_variations_and_description_from_jsonld(product_json):
    if not product_json:
        return '', {}, None, [], None

    description = product_json.get('description', '')
    if description == '*':
        description = ''

    details = {}
    images = product_json.get('image', [])
    if isinstance(images, str):
        images = [images]

    price = None
    availability = None
    offers = product_json.get('offers')
    if offers:
        if isinstance(offers, dict):
            price_str = offers.get('price')
            availability = offers.get('availability')
            try:
                price = float(price_str)
            except:
                price = None
        elif isinstance(offers, list):
            first_offer = offers[0]
            price_str = first_offer.get('price')
            availability = first_offer.get('availability')
            try:
                price = float(price_str)
            except:
                price = None

    return description, details, price, images, availability

def parse_product_description_and_variations(html):
    details = {}
    description = ''

    soup = BeautifulSoup(html, 'html.parser')
    product_details_div = soup.select_one('div#productDetails')
    if product_details_div:
        desc_div = product_details_div.select_one('div.detail-description')
        if desc_div:
            paragraphs = desc_div.find_all('p')
            desc_texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True) and p.get_text(strip=True) != '*']
            description = ' '.join(desc_texts).strip()

        product_features_div = product_details_div.select_one('div.product-features')
        if product_features_div:
            features_list = product_features_div.select('ul.features-lists li.features-lists-item')
            for feature in features_list:
                name_tag = feature.find('h3', class_='features-lists-item-name')
                value_tag = feature.find('span', class_='features-lists-item-value')
                if name_tag and value_tag:
                    name = name_tag.get_text(strip=True)
                    value = value_tag.get_text(strip=True)
                    if value and value != '*':
                        details[name] = value

    wash_care_div = soup.select_one('div#washCare')
    if wash_care_div:
        wash_care_features = wash_care_div.select('ul.features-lists li.features-lists-item')
        wash_care_texts = []
        for feature in wash_care_features:
            value_tag = feature.find('span', class_='features-lists-item-value')
            if value_tag:
                text = value_tag.get_text(strip=True)
                if text and text != '*':
                    wash_care_texts.append(text)
        if wash_care_texts:
            wash_care_desc = ' '.join(wash_care_texts).strip()
            if description:
                description += '\n\nWash & Care:\n' + wash_care_desc
            else:
                description = 'Wash & Care:\n' + wash_care_desc

    return description, details

def parse_products_from_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            logger.error(f"Error loading page {url}: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        product_tiles = soup.find_all('div', class_='product-tile')

        if not product_tiles:
            logger.info("No products found on page, maybe end of pagination.")
            return []

        for tile in product_tiles:
            product = {}
            a_tag = tile.find('a', href=True)
            if a_tag:
                href = a_tag['href']
                product['product_url'] = 'https://www.biba.in' + href if href.startswith('/') else href
                img = a_tag.find('img', alt=True)
                product['product_name'] = img['alt'].split(" image number")[0] if img else None
            else:
                product['product_url'] = None
                product['product_name'] = None

            product_id = tile.get('id')
            if not product_id:
                product_id = str(random.randint(1000000, 9999999))
            product['product_id'] = product_id

            product['image_urls'] = []

            product['brand'] = 'Biba'

            products.append(product)
        return products

    except Exception as e:
        logger.error(f"Error parsing page {url}: {e}")
        return []

def fetch_product_details(product):
    product_url = product.get('product_url')
    description = ''
    variations = {}
    images = []
    price = None
    availability = None

    try:
        response = requests.get(product_url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            product_json = parse_json_ld(response.text)
            desc_json, var_json, price, images, availability = '', {}, None, [], None
            if product_json:
                desc_json, var_json, price, images, availability = parse_product_variations_and_description_from_jsonld(product_json)
            if not desc_json and not var_json:
                desc_html, var_html = parse_product_description_and_variations(response.text)
                if desc_html:
                    desc_json = desc_html
                if var_html:
                    var_json = var_html

            description = desc_json
            variations = var_json
        else:
            logger.error(f"Failed to load product page: {product_url}")
    except Exception as e:
        logger.error(f"Error loading product page {product_url}: {e}")

    product['description'] = description
    product['variations'] = variations
    product['price'] = price
    product['availability'] = availability
    product['image_urls'] = images

    logger.info(f"Product: {product.get('product_name')}")
    logger.info(f" URL: {product.get('product_url')}")
    logger.info(f" Brand: {product.get('brand')}")
    logger.info(f" Price: {product.get('price')}")
    logger.info(f" Availability: {product.get('availability')}")
    logger.info(f" Description: {product.get('description')}")
    logger.info(f" Images count: {len(images)}")
    logger.info(f" Variations:")
    for k, v in variations.items():
        logger.info(f"   - {k}: {v}")
    logger.info("-" * 40)

    return product

def remove_duplicates(products, key='product_url'):
    seen = set()
    unique_products = []
    for product in products:
        identifier = product.get(key)
        if identifier and identifier not in seen:
            unique_products.append(product)
            seen.add(identifier)
    return unique_products


def save_product_to_db(product_data):
    try:
        brand, _ = Brand.objects.get_or_create(name='Biba')
        slug = slugify(product_data.get('product_name', 'default-slug'))
        sku = product_data.get('product_id')

        availability = product_data.get('availability', '')
        availability_mapping = {
            "http://schema.org/InStock": "in_stock",
            "http://schema.org/OutOfStock": "out_of_stock",
            "http://schema.org/PreOrder": "preorder",
            "http://schema.org/Discontinued": "discontinued"
        }
        stock_status = availability_mapping.get(availability, "in_stock")

        product_obj, created = Product.objects.update_or_create(
            sku=sku,
            defaults={
                'name': product_data.get('product_name', 'No Name'),
                'slug': slug,
                'brand': brand,
                'desc': product_data.get('description', ''),
                'price': product_data.get('price'),
                'stock_status': stock_status,
            }
        )

        # Сохраняем первое изображение в поле image модели Product
        image_urls = product_data.get('image_urls', [])
        if image_urls:
            image_url = image_urls[0]
            try:
                img_temp = BytesIO(urllib.request.urlopen(image_url).read())
                img_filename = image_url.split('/')[-1].split('?')[0]
                product_obj.image.save(img_filename, File(img_temp), save=True)
            except Exception as e:
                logger.error(f"Error saving product image for {sku}: {e}")

        variations = product_data.get('variations', {})
        color = variations.get('Color', '') or variations.get('Colour', '') or ''
        size = variations.get('Size', '') or ''
        variant_sku = variations.get('SKU', sku)

        quantity = 0

        product_variant, variant_created = ProductVariant.objects.update_or_create(
            product=product_obj,
            sku=variant_sku,
            defaults={
                'description': product_data.get('description', ''),
                'color': color,
                'size': size,
                'price': product_data.get('price'),
                'quantity': quantity,
            }
        )

        # Можно также сохранить изображение вариации (если есть)
        if len(image_urls) > 1:
            variant_image_url = image_urls[1]
            try:
                img_temp = BytesIO(urllib.request.urlopen(variant_image_url).read())
                img_filename = variant_image_url.split('/')[-1].split('?')[0]
                product_variant.image.save(img_filename, File(img_temp), save=True)
            except Exception as e:
                logger.error(f"Error saving variant image for {variant_sku}: {e}")

        logger.info(f"Product saved to DB: {product_obj.name}")
        return product_obj
    except Exception as e:
        logger.error(f"Error saving product {product_data.get('product_name')}: {e}")
        return None


def save_products_to_csv(products, filename='csv_files/biba_products.csv', limit=None):
    fieldnames = ['product_url', 'product_name', 'product_id', 'image_urls', 'brand',
                  'description', 'price', 'availability', 'variations']

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        # Ограничение на количество товаров для записи в CSV (если указано)
        to_write = products if limit is None else products[:limit]

        for product in to_write:
            row = product.copy()
            row['image_urls'] = ', '.join(product.get('image_urls', []))
            row['variations'] = json.dumps(product.get('variations', {}), ensure_ascii=False)
            writer.writerow(row)

    logger.info(f"Data successfully saved to file {filename}")

def save_products_to_json(products, filename='jsons_files/biba_products.json', limit=None):
    # Ограничение на количество товаров для записи в JSON (если указано)
    to_write = products if limit is None else products[:limit]

    # Создать папку, если не существует
    ensure_dir_exists(filename)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(to_write, f, ensure_ascii=False, indent=4)

    logger.info(f"Data successfully saved to JSON file {filename}")

def ensure_dir_exists(filepath):
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    base_url = "https://www.biba.in/jewellery/"

    all_products = []
    page = 1

    while True:
        logger.info(f"Parsing page {page}...")
        page_url = f"{base_url}?page={page}"
        products_data = parse_products_from_page(page_url)
        if not products_data:
            logger.info("Reached end of pagination.")
            break
        all_products.extend(products_data)
        page += 1
        time.sleep(0.5)

    unique_products = remove_duplicates(all_products, key='product_url')
    logger.info(f"Unique products: {len(unique_products)}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        unique_products = list(executor.map(fetch_product_details, unique_products))

    limit = None  # <-- Ограничение на запись в файлы, убрать или поставить None чтобы отключить

    for product_data in unique_products:
        save_product_to_db(product_data)

    save_products_to_csv(unique_products, limit=limit)
    save_products_to_json(unique_products, limit=limit)
