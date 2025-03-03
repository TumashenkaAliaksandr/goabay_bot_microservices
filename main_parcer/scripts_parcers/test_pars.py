import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goabay_bot.settings")
django.setup()

import requests
import json
from bs4 import BeautifulSoup
import re
from django.utils.text import slugify
from bot_app.models import Product, Category
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../media')


def download_image(url, product_name):
    try:
        response = requests.get(url, stream=True, timeout=10)  # Added timeout
        response.raise_for_status()
        filename = url.split("/")[-1].split('?')[0]
        product_name = slugify(product_name)
        filepath = os.path.join('products', f'{product_name}_{filename}')
        media_dir = os.path.join(MEDIA_ROOT, 'products')

        if not os.path.exists(media_dir):
            os.makedirs(media_dir)

        full_path = os.path.join(MEDIA_ROOT, filepath)
        with open(full_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        logging.info(f"Image downloaded successfully: {url} to {filepath}")
        return filepath
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error downloading image from {url}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error downloading image from {url}: {e}")
        return None


def collect_product_links_from_category(category_url):
    try:
        response = requests.get(category_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        product_links = set()
        product_link_pattern = re.compile(
            r'https://ishalife\.sadhguru\.org/in/(?![\w-]+/[\w-]+$)(?!bloom$)(?!terms-conditions$)(?!rudraksha-mala-beads$)(?!the-rudraksha-guide$)(?!2025-calendars-diaries$)(?!2025-calendars-diaries$)(?!clothings-accessories$)(?!home$)(?!returns$)(?!about-us$)(?!media$)(?!support-ticket$)(?!bodycare$)(?!devi-panel$)(?!rudraksha$)(?!natural-food$)(?!yogastore$)(?!temple-consecrated$)(?!privacy-policy-cookie-restriction-mode$)(?!copper-cleaning-instructions$)(?!savetheweave$)(?!marathi$)(?!store-locator$)(?!health-immunity$)(?!track-order$)(?!sso-faq$)(?!books-and-dvds$)[\w-]+$'
        )

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if product_link_pattern.match(href):
                product_links.add(href)

        return list(product_links)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error for {category_url}: {e}")
        return []
    except Exception as e:
        logging.error(f"Parsing error for {category_url}: {e}")
        return []

def parse_isha_product(html_content, product_url):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        data = {}

        # Название
        title_element = soup.find('span', class_='base', attrs={'data-ui-id': 'page-title-wrapper'})
        raw_name = title_element.text.strip() if title_element else "Название не найдено"
        # Convert to ASCII only
        name = ''.join(char for char in raw_name if char.isalnum() or char.isspace())
        data['название'] = name

        # Ссылка на товар
        data['ссылка на товар'] = product_url

        # Цена
        price = None
        price_box = soup.find('div', class_='product-info-price')
        if price_box:
            special_price = price_box.find('span', class_='price-wrapper')
            if special_price:
                price_wrapper = special_price.find('span', class_='price')
                if price_wrapper:
                    price_str = price_wrapper.text.replace('₹', '').replace('&nbsp;', '').strip()
                    try:
                        price = float(re.sub(r'[^\d\.]', '', price_str))
                    except ValueError:
                        logging.error(f"Could not convert price to float: {price_str}")
                        price = None
        data['цена'] = price if price is not None else 0.0

        # Описание
        product_details_div = soup.find("div", class_="product-short-info-content")
        description = ""
        if product_details_div:
            details_h3 = product_details_div.find("h3", string="Product Details")
            if details_h3:
                details_span = details_h3.find_parent("div").find("span")
                if details_span:
                    details_text = details_span.get_text(separator="\n", strip=True)
                    description += "Product Details:\n" + details_text + "\n\n"

            description_h3 = product_details_div.find("h3", string="Product Description")
            if description_h3:
                description_span = description_h3.find_parent("div").find("span")
                if description_span:
                    description_text = description_span.get_text(separator="\n", strip=True)
                    description += "Product Description:\n" + description_text + "\n\n"

            more_info_h3 = product_details_div.find("h3", string="More Information")
            if more_info_h3:
                more_info_span = more_info_h3.find_parent("div").find("span")
                if more_info_span:
                    more_info_text = more_info_span.get_text(separator="\n", strip=True)
                    description += "More Information:\n" + more_info_text + "\n\n"
        data['описание'] = description.strip()
        desc = data['описание']

        # Images
        image_url = None
        magic_toolbox = soup.find('div', class_='MagicToolboxContainer')
        if magic_toolbox:
            image_link = magic_toolbox.find('a', class_='MagicZoom')
            if image_link:
                image_url = image_link['href']
        data['фото'] = image_url if image_url else "Фото не найдено"

        # Категория и подкатегории
        breadcrumbs_div = soup.find('div', class_='breadcrumbs')
        if breadcrumbs_div:
            breadcrumb_links = breadcrumbs_div.find_all('a', class_='arv')
            categories = [link.text.strip() for link in breadcrumb_links]
            data['категория'] = categories[0] if categories else "Категория не определена"
            data['подкатегория'] = categories[1:] if len(categories) > 1 else []
        else:
            data['категория'] = "Категория не определена"
            data['подкатегория'] = []

        # Производитель
        data['производитель'] = "Isha Life"

        # Размер
        data['размер'] = "100 капсул"

        # Доставка
        shipping_info = []
        shipping_wrap = soup.find('div', class_='shipping-wrap')
        if shipping_wrap:
            shipping_blocks = shipping_wrap.find_all('div', class_='shipping-block')
            for block in shipping_blocks:
                text = block.find('p').text.strip()
                shipping_info.append(text)
        data['доставка'] = shipping_info if shipping_info else "Информация о доставке не найдена"

        # SKU
        sku = None
        more_info_table = soup.find('table', class_='data table additional-attributes')
        if more_info_table:
            sku_row = more_info_table.find('tr')
            if sku_row:
                sku_label_cell = sku_row.find('td', class_='col label sku')
                sku_data_cell = sku_row.find('td', class_='col data sku')
                if sku_label_cell and sku_data_cell:
                    if sku_label_cell.text.strip() == 'SKU:':
                        sku = sku_data_cell.text.strip()

        data['SKU'] = sku if sku else "SKU не найден"

        # Рейтинг
        rating_summary = soup.find('div', class_='rating-summary')
        if rating_summary:
            rating_result = rating_summary.find('div', class_='rating-result')
            if rating_result:
                title = rating_result['title']
                # Extract the percentage from the title
                rating_percentage = title.replace('%', '').strip()
                try:
                    rating = float(rating_percentage)
                except ValueError:
                    rating = 0.0
                data['rating'] = str(rating)
                print(f"Rating: {rating}")
            else:
                data['rating'] = "0"
                print("Rating result not found")
        else:
            data['rating'] = "0"
            print("Rating summary not found")

        return data, name, price, desc, image_url

    except Exception as e:
        logging.error(f"Error parsing product {product_url}: {e}")
        return None, None, None, None, None


def save_product_to_db(data, name, price, desc, image_url):
    try:
        # Сохраняем в базу данных
        category_name = data['категория'] if data['категория'] else "General"
        category, created = Category.objects.get_or_create(name=category_name)

        cleaned_name = re.sub(r'[\(\)\.\-]', ' ', name).strip()
        cleaned_name = re.sub(r'[^\w\s]', '', cleaned_name)
        slug = cleaned_name.replace(' ', '-').lower()

        # Загружаем изображение и получаем путь к нему
        image_path = download_image(image_url, name) if image_url else None

        # Get existing product or create a new one
        product, created = Product.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'desc': desc,
                'price': price,
                'image': image_path,
                'rating': data['rating'],  # Use parsed rating
            }
        )

        # Обновить поля, если продукт уже существует
        if not created:
            product.name = name
            product.desc = desc
            product.price = price
            product.image = image_path
            product.rating = data['rating']  # Update rating
            product.save()
            logging.info(f"Product updated in database: {name} (Slug: {slug})")
        else:
            logging.info(f"Product saved to database: {name} (Slug: {slug})")

        product.category.clear()
        product.category.add(category)

    except Exception as e:
        logging.error(f"Error saving product {name} to database: {e}")


def collect_all_product_links(category_urls):
    all_product_links = set()
    for url in category_urls:
        product_links = collect_product_links_from_category(url)
        all_product_links.update(product_links)
    return list(all_product_links)


if __name__ == '__main__':
    category_urls = [
        'https://ishalife.sadhguru.org/in/rudraksha',
        'https://ishalife.sadhguru.org/in/rudraksha/consecrated-panchamukhi-malas',
        'https://ishalife.sadhguru.org/in/rudraksha/consecrated-rudraksha-beads',
        'https://ishalife.sadhguru.org/in/temple-consecrated',
        'https://ishalife.sadhguru.org/in/rudraksha/spatik-malas',
        'https://ishalife.sadhguru.org/in/temple-consecrated',
        'https://ishalife.sadhguru.org/in/yogastore',
        'https://ishalife.sadhguru.org/in/natural-food',
        'https://ishalife.sadhguru.org/in/health-immunity',
        'https://ishalife.sadhguru.org/in/clothings-accessories',
        'https://ishalife.sadhguru.org/in/bodycare',
        'https://ishalife.sadhguru.org/in/home',
        'https://ishalife.sadhguru.org/in/media/books',
        'https://ishalife.sadhguru.org/in/media',
        'https://ishalife.sadhguru.org/in/media/books/marathi',
        'https://ishalife.sadhguru.org/in/devi-panel',
        'https://ishalife.sadhguru.org/in/2025-calendars-diaries',
    ]

    product_links = collect_all_product_links(category_urls)
    print(f"Найдено {len(product_links)} ссылок на продукты.")

    all_products_data = []
    for product_url in product_links:
        try:
            response = requests.get(product_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch {product_url}: {e}")
            continue

        product_data, name, price, desc, image_url = parse_isha_product(html_content, product_url)
        if product_data:
            all_products_data.append(product_data)
            print(f"Информация о продукте успешно спарсена с {product_url}")
            save_product_to_db(product_data, name, price, desc, image_url)
        else:
            print(f"Не удалось получить информацию о продукте с {product_url}")

    with open('jsons/product_ishalife.json', 'w', encoding='utf-8') as f:
        json.dump(all_products_data, f, indent=4, ensure_ascii=False)

    print("Данные о продуктах сохранены в product_ishalife.json")
