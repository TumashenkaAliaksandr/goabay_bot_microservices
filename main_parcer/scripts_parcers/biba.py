import csv
import requests
from bs4 import BeautifulSoup
import time
import json
import concurrent.futures
import logging
import random

# Логирование
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

def parse_product_variations_and_description(html):
    details = {}
    description = ''

    soup = BeautifulSoup(html, 'html.parser')
    product_details_div = soup.select_one('div#productDetails')
    if not product_details_div:
        logger.debug("productDetails block not found in html")
        return description, details

    desc_div = product_details_div.select_one('div.detail-description')
    if desc_div:
        paragraphs = desc_div.find_all('p')
        desc_texts = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and text != '*':
                desc_texts.append(text)
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

            image_tags = tile.select('div.carousel-inner img')
            product['image_urls'] = [img['src'] for img in image_tags if img.has_attr('src')]

            rating_span = tile.select_one('div.rating span.sr-only')
            product['rating'] = rating_span.get_text(strip=True) if rating_span else None

            product['brand'] = 'Biba'

            quickview_tag = tile.find('a', class_='quickview')
            if quickview_tag and quickview_tag.has_attr('data-url'):
                product['quickview_url'] = 'https://www.biba.in' + quickview_tag['data-url']
            else:
                product['quickview_url'] = None

            products.append(product)

        return products

    except Exception as e:
        logger.error(f"Error parsing page {url}: {e}")
        return []

def fetch_product_details(product):
    product_url = product.get('product_url')

    try:
        response = requests.get(product_url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            description, variations = parse_product_variations_and_description(response.text)
            product['description'] = description
            product['variations'] = variations
        else:
            product['description'] = ''
            product['variations'] = {}
            logger.error(f"Failed to load product page: {product_url}")
    except Exception as e:
        product['description'] = ''
        product['variations'] = {}
        logger.error(f"Error loading product page {product_url}: {e}")

    logger.info(f"Product: {product.get('product_name')}")
    logger.info(f" URL: {product.get('product_url')}")
    logger.info(f" Rating: {product.get('rating')}")
    logger.info(f" Brand: {product.get('brand')}")
    logger.info(f" Description: {product.get('description')}")
    logger.info(f" Variations:")
    for k, v in product.get('variations', {}).items():
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

def save_products_to_csv(products, filename='csv_files/biba_products.csv'):
    fieldnames = ['product_url', 'product_name', 'product_id', 'image_urls', 'rating', 'quickview_url', 'brand',
                  'description', 'variations']

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for product in products:
            row = product.copy()
            row['image_urls'] = ', '.join(product.get('image_urls', []))
            row['variations'] = json.dumps(product.get('variations', {}), ensure_ascii=False)
            writer.writerow(row)

    logger.info(f"Data successfully saved to file {filename}")

if __name__ == "__main__":
    base_url = "https://www.biba.in/intl/jewellery/"

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

    save_products_to_csv(unique_products)
