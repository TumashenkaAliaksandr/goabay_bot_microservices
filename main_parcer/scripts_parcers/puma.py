import csv
import os
from urllib.parse import urljoin

import django
import unidecode


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goabay_bot.settings")
django.setup()

import requests
import json
from bs4 import BeautifulSoup
import re
from django.utils.text import slugify
from bot_app.models import Product, ProductImage  # Импортируем модели
from site_app.models import Brand, Category
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../media')
BASE_URL = "https://in.puma.com"

def download_image(url, product_name, is_additional=False):
    """
    Скачивает изображение, сохраняет его и возвращает путь к файлу.

    Аргументы:
        url (str): URL изображения.
        product_name (str): Название продукта для создания имени файла.
        is_additional (bool): Флаг, указывающий, является ли изображение дополнительным.

    Возвращает:
        str: Путь к файлу изображения или None в случае ошибки.
    """
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        filename = os.path.basename(url).split('?')[0]  # Извлекаем имя файла из URL

        product_name = slugify(product_name)  # Преобразуем имя продукта в слаг

        # Укорачиваем имя продукта и имя файла до 50 символов
        product_name = product_name[:500]
        filename = filename[:500]

        if is_additional:
            filepath = os.path.join('products/additional', f'{product_name}_{filename}')
            media_dir = os.path.join(MEDIA_ROOT, 'products/additional')
        else:
            filepath = os.path.join('products', f'{product_name}_{filename}')
            media_dir = os.path.join(MEDIA_ROOT, 'products')

        if not os.path.exists(media_dir):
            os.makedirs(media_dir)

        full_path = os.path.join(MEDIA_ROOT, filepath)  # Полный путь к файлу
        logging.info(f"Full image path: {full_path}")

        with open(full_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        logging.info(f"Image downloaded successfully: {url} to {filepath}")
        return filepath
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при скачивании изображения с {url}: {e}")
        return None
    except Exception as e:
        logging.error(f"Ошибка при обработке изображения с {url}: {e}")
        return None


def collect_product_links_from_category(category_url):
    """
    Собирает ссылки на продукты из URL категории.

    Аргументы:
        category_url (str): URL категории.

    Возвращает:
        list: Список полных ссылок на продукты.
    """
    try:
        response = requests.get(category_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        product_links = set()

        # Находим все <li> с data-test-id="product-list-item"
        product_items = soup.find_all('li', attrs={'data-test-id': 'product-list-item'})

        for item in product_items:
            a_tag = item.find('a', attrs={'data-test-id': 'product-list-item-link'}, href=True)
            if a_tag:
                # Формируем полный URL из относительного href
                full_url = urljoin(BASE_URL, a_tag['href'])
                product_links.add(full_url)

        return list(product_links)

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к {category_url}: {e}")
        return []
    except Exception as e:
        logging.error(f"Ошибка при парсинге {category_url}: {e}")
        return []

def parse_puma_product(html_content, product_url):
    """
    Парсит HTML контент страницы продукта.

    Аргументы:
        html_content (str): HTML контент страницы продукта.
        product_url (str): URL страницы продукта.

    Возвращает:
        tuple: Кортеж с данными продукта, названием, ценой и описанием.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        data = {}

        import unicodedata

        # Получаем элемент с названием товара по новому селектору
        title_element = soup.find('h1', attrs={'data-test-id': 'pdp-title'})
        raw_name = title_element.text.strip() if title_element else "Название не найдено"

        def is_letter_digit_or_space(char):
            """
            Проверяет, является ли символ буквой (любой алфавит Unicode),
            цифрой или пробелом.
            """
            uni_category = unicodedata.category(char)
            return uni_category.startswith('L') or uni_category.startswith('N') or char.isspace()

        # Очищаем название, оставляя только буквы, цифры и пробелы
        name = ''.join(char for char in raw_name if is_letter_digit_or_space(char))

        # Убираем лишние пробелы (множественные подряд)
        name = ' '.join(name.split())

        data['Name'] = name

        # Сохраняем ссылку на товар
        data['Product urls'] = product_url

        # Получаем блок с ценой по новому селектору
        price = None
        price_region = soup.find('div', attrs={'data-test-id': 'pdp-price-region'})
        if price_region:
            # Ищем цену со скидкой (актуальную цену)
            sale_price_span = price_region.find('span', attrs={'data-test-id': 'item-sale-price-pdp'})
            if sale_price_span and sale_price_span.text.strip():
                price_str = sale_price_span.text.strip()
            else:
                # Если нет цены со скидкой, берем обычную цену
                price_span = price_region.find('span', attrs={'data-test-id': 'item-price-pdp'})
                price_str = price_span.text.strip() if price_span else None

            if price_str:
                # Убираем символы валюты и пробелы
                price_str_clean = price_str.replace('₹', '').replace(',', '').strip()
                try:
                    price = float(re.sub(r'[^\d.]', '', price_str_clean))
                except ValueError:
                    logging.error(f"Не удалось преобразовать цену в число: {price_str_clean}")
                    price = None

        data['price'] = price if price is not None else 0.0

        # Описание
        description = ""
        product_details_div = soup.find("div", attrs={"data-test-id": "pdp-product-description"})

        if product_details_div:
            # Ищем заголовок "Description" (в вашем примере это <h2> с текстом "Description")
            description_h2 = product_details_div.find(
                lambda tag: tag.name in ['h2', 'h3'] and tag.get_text(strip=True) == "Description")
            if description_h2:
                # Ищем следующий sibling с текстом описания (обычно div с текстом)
                description_div = description_h2.find_next_sibling()
                if description_div:
                    description_text = description_div.get_text(separator="\n", strip=True)
                    if description_text:
                        description += description_text + "\n\n"

            # Ищем дополнительные списки с информацией (например, ul с классом, содержащим 'list-disc')
            additional_lists = product_details_div.find_all('ul', class_=lambda x: x and 'list-disc' in x)
            for ul in additional_lists:
                ul_texts = []
                for li in ul.find_all('li'):
                    li_text = li.get_text(strip=True)
                    if li_text:
                        ul_texts.append(f"- {li_text}")
                if ul_texts:
                    description += "Additional Information:\n" + "\n".join(ul_texts) + "\n\n"

        data['descriptions'] = description.strip()

        # Добавляем извлечение additional_description
        additional_description = ""
        product_options_wrapper = soup.find('div', class_='product-options-wrapper')
        if product_options_wrapper:
            customize_title = product_options_wrapper.find('span', id='customizeTitle')
            if customize_title:
                additional_description += f"Customize: {customize_title.text.strip()}\n"

            bundle_options = product_options_wrapper.find_all('div', class_='field choice')
            for option in bundle_options:
                label = option.find('label', class_='label')
                if label:
                    additional_description += f"- {label.text.strip()}\n"

        data['additional_description'] = additional_description.strip()
        desc = data['descriptions']

        # Добавляем извлечение additional_description
        additional_description = ""
        product_options_wrapper = soup.find('div', class_='product-options-wrapper')
        if product_options_wrapper:
            customize_title = product_options_wrapper.find('span', id='customizeTitle')
            if customize_title:
                additional_description += f"Customize: {customize_title.text.strip()}\n"

            bundle_options = product_options_wrapper.find_all('div', class_='field choice')
            for option in bundle_options:
                label = option.find('label', class_='label')
                if label:
                    additional_description += f"- {label.text.strip()}\n"

        data['additional_description'] = additional_description.strip()

        # Images
        image_urls = []
        gallery_section = soup.find('section', attrs={'data-test-id': 'product-image-gallery-section'})
        if gallery_section:
            # Ищем все <img> внутри секции галереи
            img_tags = gallery_section.find_all('img')
            for img in img_tags:
                # Берём src только если он начинается с http (или https)
                src = img.get('src')
                if src and src.startswith('http'):
                    image_urls.append(src)
        data['image_urls'] = image_urls  # Сохраняем все URL изображений

        # Категория и подкатегории
        breadcrumbs_div = soup.find('div', class_='breadcrumbs')
        if breadcrumbs_div:
            breadcrumb_links = breadcrumbs_div.find_all('a', class_='arv')
            categories = [link.text.strip() for link in breadcrumb_links]
            data['Category'] = categories[0] if categories else "Категория не определена"
            data['Subcategory'] = categories[1:] if len(categories) > 1 else []
        else:
            data['Category'] = "Категория не определена"
            data['Subcategory'] = []

        # Производитель
        data['Brand'] = "Puma"

        # Размер
        data['Sizes'] = "100 капсул"

        # Доставка
        shipping_info = []
        shipping_wrap = soup.find('div', class_='shipping-wrap')
        if shipping_wrap:
            shipping_blocks = shipping_wrap.find_all('div', class_='shipping-block')
            for block in shipping_blocks:
                text = block.find('p').text.strip()
                shipping_info.append(text)
        data['Delivery'] = shipping_info if shipping_info else "Информация о доставке не найдена"

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

        return data, name, price, desc

    except Exception as e:
        logging.error(f"Ошибка при парсинге продукта {product_url}: {e}")
        return None, None, None, None


def save_product_to_db(data, name, price, desc):
    try:
        logging.info(f"Начало сохранения продукта: {name}")

        category_name = data.get('Category') or "General"
        category, created = Category.objects.get_or_create(name=category_name)
        logging.info(f"Категория {'создана' if created else 'уже существует'}: {category}")

        cleaned_name = unidecode.unidecode(name)
        cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_name).strip()[:100]
        slug = cleaned_name.replace(' ', '-').lower()
        logging.info(f"Очищенное имя: {cleaned_name}, slug: {slug}")

        brand_name = data.get('Brand') or 'Puma'
        brand, brand_created = Brand.objects.get_or_create(
            name=brand_name,
            defaults={'slug': slugify(brand_name)}
        )
        logging.info(f"Бренд {'создан' if brand_created else 'уже существует'}: {brand}")

        image_urls = data.get('image_urls', [])
        main_image_url = image_urls[0] if image_urls else None
        main_image_path = download_image(main_image_url, slug) if main_image_url else None
        logging.info(f"Путь к изображению: {main_image_path}")

        product, created = Product.objects.get_or_create(
            slug=slug,
            defaults={
                'name': cleaned_name,
                'desc': desc,
                'price': price,
                'image': main_image_path,
                'rating': data.get('rating', '0'),
                'additional_description': data.get('additional_description', ''),
                'brand': brand
            }
        )

        if not created:
            # Обновляем поля и сохраняем
            product.name = cleaned_name
            product.desc = desc
            product.price = price
            if main_image_path:
                product.image = main_image_path
            product.rating = data.get('rating', '0')
            product.additional_description = data.get('additional_description', '')
            product.brand = brand
            product.save()
            logging.info(f"Продукт обновлен: {product}")

        # Дополнительные изображения
        if len(image_urls) > 1:
            logging.info(f"Найдено {len(image_urls) - 1} дополнительных изображений")
            for img_url in image_urls[1:]:
                try:
                    additional_image_path = download_image(img_url, slug, is_additional=True)
                    if additional_image_path:
                        if not ProductImage.objects.filter(product=product, image=additional_image_path).exists():
                            ProductImage.objects.create(product=product, image=additional_image_path)
                            logging.info(f"Добавлено изображение: {additional_image_path}")
                except Exception as e:
                    logging.error(f"Ошибка при добавлении изображения: {e}")

        # Обновляем категории
        product.category.clear()
        product.category.add(category)
        logging.info(f"Добавлена категория {category} к продукту")

        return True
    except Exception as e:
        logging.error(f"КРИТИЧЕСКАЯ ОШИБКА при сохранении продукта {name}: {e}", exc_info=True)
        return False


def collect_all_product_links(category_urls):
    """
    Собирает все ссылки на продукты из списка URL категорий.

    Аргументы:
        category_urls (list): Список URL категорий.

    Возвращает:
        list: Список всех ссылок на продукты.
    """
    all_product_links = set()
    for url in category_urls:
        product_links = collect_product_links_from_category(url)
        all_product_links.update(product_links)
    return list(all_product_links)


if __name__ == '__main__':
    category_urls = [
        'https://in.puma.com/in/en/mens',

    ]

    product_links = collect_all_product_links(category_urls)  # Собираем ссылки на продукты
    print(f"Найдено {len(product_links)} ссылок на продукты.")

    all_products_data = []  # Список для хранения данных о всех продуктах
    for product_url in product_links:
        try:
            response = requests.get(product_url, timeout=10)  # Отправляем GET запрос к URL продукта
            response.raise_for_status()  # Проверяем статус ответа

            html_content = response.text  # Получаем HTML контент страницы

        except requests.exceptions.RequestException as e:
            logging.error(f"Не удалось получить {product_url}: {e}")  # Обрабатываем ошибку запроса
            continue

        product_data, name, price, desc = parse_puma_product(html_content, product_url)  # Парсим данные продукта
        if product_data:
            all_products_data.append(product_data)  # Добавляем данные продукта в список
            print(f"Информация о продукте успешно спарсена с {product_url}")
            save_product_to_db(product_data, name, price, desc)  # Сохраняем данные продукта в базу данных
        else:
            print(f"Не удалось получить информацию о продукте с {product_url}")

    with open('jsons/product_puma.json', 'w', encoding='utf-8') as f:
        json.dump(all_products_data, f, indent=4, ensure_ascii=False)  # Сохраняем данные в JSON файл

    print("Данные о продуктах сохранены в product_puma.json")

    csv_file = 'jsons/product_puma.csv'

    if all_products_data:
        # Преобразуем поля с списками в строки без скобок
        for product in all_products_data:
            # Обработка поля с ссылками на изображения
            if isinstance(product.get('image_urls'), list):
                product['image_urls'] = ', '.join(product['image_urls'])
            # Обработка поля подкатегорий (с заглавной буквы)
            if isinstance(product.get('Subcategory'), list):
                product['Subcategory'] = ', '.join(product['Subcategory'])
            # Обработка поля доставки (с заглавной буквы)
            if isinstance(product.get('Delivery'), list):
                product['Delivery'] = ', '.join(product['Delivery'])

        # Получаем заголовки из ключей первого словаря
        fieldnames = all_products_data[0].keys()

        with open(csv_file, 'w', newline='', encoding='utf-8') as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_products_data)
    else:
        print("Данные для CSV пусты, файл не создан.")

