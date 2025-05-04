import requests
from bs4 import BeautifulSoup
import re

# Ключевые слова для поиска
KEYWORDS = {
    'name': ['name', 'title', 'product-name', 'product_title', 'item-name', 'prod-name'],
    'price': ['price', 'cost', 'amount', 'product-price', 'prod-price'],
    'description': ['description', 'desc', 'product-description', 'prod-desc', 'details'],
}

def has_keyword(attr_value, keywords):
    if not attr_value:
        return False
    if isinstance(attr_value, list):
        attr_value = ' '.join(attr_value)
    attr_value = attr_value.lower()
    return any(k in attr_value for k in keywords)

def find_element_by_keywords(soup, keywords):
    for cls in keywords:
        el = soup.find(attrs={'class': re.compile(cls, re.I)})
        if el:
            return el
    for id_key in keywords:
        el = soup.find(attrs={'id': re.compile(id_key, re.I)})
        if el:
            return el
    return None

def parse_product_block(block):
    data = {}
    for key, keywords in KEYWORDS.items():
        el = find_element_by_keywords(block, keywords)
        if el:
            data[key] = el.get_text(strip=True)
        else:
            data[key] = None
    return data

def parse_products_from_page(url, product_container_keywords=['product', 'item', 'card', 'listing']):
    print(f"Парсим сайт: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')

    product_blocks = []
    for keyword in product_container_keywords:
        found_blocks = soup.find_all(attrs={'class': re.compile(keyword, re.I)})
        product_blocks.extend(found_blocks)

    if not product_blocks:
        for keyword in product_container_keywords:
            found_blocks = soup.find_all(attrs={'id': re.compile(keyword, re.I)})
            product_blocks.extend(found_blocks)

    product_blocks = list(set(product_blocks))

    print(f"Найдено блоков товаров: {len(product_blocks)}")

    products = []
    for block in product_blocks:
        product_data = parse_product_block(block)
        if any(product_data.values()):
            products.append(product_data)

    return products

if __name__ == '__main__':
    urls = [
        'https://www.rippletea.com/shop',
        'https://ridersarena.com/products/',
        'https://toycra.com/products',
        # добавьте сюда другие URL сайтов
    ]

    for url in urls:
        try:
            products = parse_products_from_page(url)
            print(f"Товары с сайта {url}:")
            for i, product in enumerate(products, 1):
                print(f"Товар {i}:")
                for k, v in product.items():
                    print(f"  {k}: {v}")
                print('-' * 40)
        except requests.exceptions.HTTPError as e:
            print(f"Ошибка HTTP при запросе {url}: {e}")
        except Exception as e:
            print(f"Ошибка при парсинге {url}: {e}")
