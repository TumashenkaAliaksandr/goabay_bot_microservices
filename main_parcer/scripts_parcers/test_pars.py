import os
import django
import unidecode

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goabay_bot.settings")
django.setup()

import requests
import json
from bs4 import BeautifulSoup
import re
from django.utils.text import slugify
from bot_app.models import Product, Category, ProductImage  # Импортируем модели
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../media')


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
        product_name = product_name[:50]
        filename = filename[:50]

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
        list: Список ссылок на продукты.
    """
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
        logging.error(f"Ошибка при запросе к {category_url}: {e}")
        return []
    except Exception as e:
        logging.error(f"Ошибка при парсинге {category_url}: {e}")
        return []


def parse_isha_product(html_content, product_url):
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

        # Название
        title_element = soup.find('span', class_='base', attrs={'data-ui-id': 'page-title-wrapper'})
        raw_name = title_element.text.strip() if title_element else "Название не найдено"
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
                        logging.error(f"Не удалось преобразовать цену в число: {price_str}")
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
        magic_toolbox = soup.find('div', class_='MagicToolboxContainer')
        if magic_toolbox:
            image_links = magic_toolbox.find_all('a', class_='MagicZoom')
            for link in image_links:
                image_urls.append(link['href'])
        data['image_urls'] = image_urls  # Сохраняем все URL изображений

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

        return data, name, price, desc

    except Exception as e:
        logging.error(f"Ошибка при парсинге продукта {product_url}: {e}")
        return None, None, None, None


def save_product_to_db(data, name, price, desc):
    """
    Сохраняет данные продукта в базу данных.

    Аргументы:
        data (dict): Словарь с данными продукта.
        name (str): Название продукта.
        price (float): Цена продукта.
        desc (str): Описание продукта.
    """
    try:
        # Сохраняем в базу данных
        category_name = data['категория'] if data['категория'] else "General"
        category, created = Category.objects.get_or_create(name=category_name)

        # Логируем длину названия перед очисткой
        logging.info(f"Длина оригинального названия: {len(name)}")

        # Преобразуем не-ASCII символы и создаем слаг
        cleaned_name = unidecode.unidecode(name)
        cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_name).strip()[:100]  # Обрезаем до 100 символов

        # Логируем длину названия после очистки
        logging.info(f"Длина очищенного названия: {len(cleaned_name)}")

        # Создаем слаг на основе очищенного названия
        slug = cleaned_name.replace(' ', '-').lower()

        # Получаем URL изображений
        image_urls = data.get('image_urls', [])
        main_image_url = image_urls[0] if image_urls else None

        # Скачиваем основное изображение
        main_image_path = download_image(main_image_url, slug) if main_image_url else None

        # Пытаемся получить существующий продукт или создать новый
        product, created = Product.objects.get_or_create(
            slug=slug,
            defaults={
                'name': cleaned_name,
                'desc': desc,
                'price': price,
                'image': main_image_path,
                'rating': data['rating'],
                'additional_description': data['additional_description'],
            }
        )

        if created:
            logging.info(f"Продукт создан в базе данных: {cleaned_name} (Slug: {slug})")
        else:
            logging.info(f"Продукт уже существует в базе данных: {cleaned_name} (Slug: {slug})")
        # Обрабатываем дополнительные изображения
        processed_images = set()  # Отслеживаем обработанные URL, чтобы избежать дубликатов

        for img_url in image_urls[1:]:  # Пропускаем первое изображение, так как оно основное
            if img_url not in processed_images:  # Проверяем, не было ли изображение уже обработано
                try:
                    additional_image_path = download_image(img_url, slug,
                                                           is_additional=True)  # Скачиваем дополнительное изображение

                    if additional_image_path:
                        # Проверяем, существует ли уже такое изображение перед созданием
                        if not ProductImage.objects.filter(product=product, image=additional_image_path).exists():
                            ProductImage.objects.create(product=product, image=additional_image_path)
                            logging.info(f"Дополнительное изображение сохранено для продукта {cleaned_name}")
                        else:
                            logging.info(f"Дубликат дополнительного изображения пропущен: {img_url}")
                    else:
                        logging.warning(
                            f"Не удалось скачать дополнительное изображение с {img_url} для продукта {cleaned_name}")

                except Exception as e:
                    logging.error(
                        f"Ошибка при сохранении дополнительного изображения для продукта {cleaned_name} с {img_url}: {e}")

                processed_images.add(img_url)  # Добавляем URL изображения в набор обработанных
            else:
                logging.info(f"Пропускаем дубликат изображения: {img_url} для продукта {cleaned_name}")

        product.category.clear()
        product.category.add(category)

    except Exception as e:
        logging.error(f"Ошибка при сохранении продукта {cleaned_name} в базу данных: {e}")


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

        product_data, name, price, desc = parse_isha_product(html_content, product_url)  # Парсим данные продукта
        if product_data:
            all_products_data.append(product_data)  # Добавляем данные продукта в список
            print(f"Информация о продукте успешно спарсена с {product_url}")
            save_product_to_db(product_data, name, price, desc)  # Сохраняем данные продукта в базу данных
        else:
            print(f"Не удалось получить информацию о продукте с {product_url}")

    with open('jsons/product_ishalife.json', 'w', encoding='utf-8') as f:
        json.dump(all_products_data, f, indent=4, ensure_ascii=False)  # Сохраняем данные в JSON файл

    print("Данные о продуктах сохранены в product_ishalife.json")
