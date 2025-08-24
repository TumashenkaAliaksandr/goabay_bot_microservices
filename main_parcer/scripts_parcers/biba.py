import csv
import requests
from bs4 import BeautifulSoup

def parse_products_from_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка при загрузке страницы: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    products = []

    product_tiles = soup.find_all('div', class_='product-tile')

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

        product['product_id'] = tile.get('id')

        image_tags = tile.select('div.carousel-inner img')
        product['image_urls'] = [img['src'] for img in image_tags if img.has_attr('src')]

        rating_span = tile.select_one('div.rating span.sr-only')
        product['rating'] = rating_span.get_text(strip=True) if rating_span else None

        quickview_tag = tile.find('a', class_='quickview')
        if quickview_tag and quickview_tag.has_attr('data-url'):
            product['quickview_url'] = 'https://www.biba.in' + quickview_tag['data-url']
        else:
            product['quickview_url'] = None

        products.append(product)

    return products


def save_products_to_csv(products, filename='csv_files/biba_products.csv'):
    fieldnames = ['product_url', 'product_name', 'product_id', 'image_urls', 'rating', 'quickview_url']

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for product in products:
            row = product.copy()
            row['image_urls'] = ', '.join(product.get('image_urls', []))  # Преобразуем список в строку
            writer.writerow(row)

    print(f"Данные успешно сохранены в файл {filename}")


if __name__ == "__main__":
    url = "https://www.biba.in/intl/jewellery/"
    products_data = parse_products_from_page(url)

    for pd in products_data:
        print(pd)

    print(f"Всего товаров на странице: {len(products_data)}")

    save_products_to_csv(products_data)
