# import csv
# import os
# from urllib.parse import urljoin
#
# import django
# import unidecode
#
# from main_parcer.scripts_parcers.categories import CATEGORIES
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goabay_bot.settings")
# django.setup()
#
# import requests
# import json
# from bs4 import BeautifulSoup
# import re
# from django.utils.text import slugify
# from bot_app.models import Product, ProductImage  # Импортируем модели
# from site_app.models import Brand, Category
# import logging
#
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#
# MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../media')
# BASE_URL = "https://in.puma.com"
#
# def generate_unique_slug(base_slug):
#     slug = base_slug
#     counter = 1
#     while Product.objects.filter(slug=slug).exists():
#         slug = f"{base_slug}-{counter}"
#         counter += 1
#     return slug
#
# def sanitize_filename(filename):
#     filename = filename.replace('’', "'")
#     filename = re.sub(r'[^\x00-\x7F]+', '', filename)  # удаляем все не-ASCII символы
#     filename = re.sub(r'[^\w\-_\.]', '', filename)     # удаляем специальные символы
#     return filename
#
# def download_image(url, product_name, is_additional=False):
#     try:
#         response = requests.get(url, stream=True, timeout=15)
#         response.raise_for_status()
#
#         # Получаем имя файла и расширение
#         original_filename = os.path.basename(url.split("?")[0])
#         name_part, ext = os.path.splitext(original_filename)
#
#         ext = ext if ext.lower() in ['.jpg', '.jpeg', '.png', '.webp'] else '.jpg'
#
#         # Слаг для продукта
#         product_slug = slugify(product_name)[:40]  # ограничиваем длину
#         filename_clean = sanitize_filename(name_part)[:80]  # ограничиваем длину имени файла
#
#         # Только одна часть имени (либо slug, либо clean filename)
#         final_filename = f"{product_slug}{ext}"  # используем только slug для имени файла
#
#         # Путь для сохранения
#         subfolder = 'products/additional' if is_additional else 'products'
#         media_dir = os.path.join(MEDIA_ROOT, subfolder)
#         filepath = os.path.join(subfolder, final_filename)
#         full_path = os.path.join(MEDIA_ROOT, filepath)
#
#         os.makedirs(media_dir, exist_ok=True)
#
#         # Сохраняем файл
#         with open(full_path, 'wb') as f:
#             for chunk in response.iter_content(1024):
#                 f.write(chunk)
#
#         logging.info(f"Изображение сохранено: {filepath}")
#         return filepath
#
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Ошибка при скачивании изображения с {url}: {e}")
#         return None
#     except Exception as e:
#         logging.error(f"Ошибка при обработке изображения с {url}: {e}")
#         return None
#
# def collect_product_links_from_category(category_url):
#     """
#     Собирает ссылки на продукты из URL категории.
#
#     Аргументы:
#         category_url (str): URL категории.
#
#     Возвращает:
#         list: Список полных ссылок на продукты.
#     """
#     try:
#         response = requests.get(category_url, timeout=10)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.content, 'html.parser')
#         product_links = set()
#
#         # Находим все <li> с data-test-id="product-list-item"
#         product_items = soup.find_all('li', attrs={'data-test-id': 'product-list-item'})
#
#         for item in product_items:
#             a_tag = item.find('a', attrs={'data-test-id': 'product-list-item-link'}, href=True)
#             if a_tag:
#                 # Формируем полный URL из относительного href
#                 full_url = urljoin(BASE_URL, a_tag['href'])
#                 product_links.add(full_url)
#
#         return list(product_links)
#
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Ошибка при запросе к {category_url}: {e}")
#         return []
#     except Exception as e:
#         logging.error(f"Ошибка при парсинге {category_url}: {e}")
#         return []
#
# def parse_puma_product(html_content, product_url):
#     """
#     Парсит HTML контент страницы продукта.
#
#     Аргументы:
#         html_content (str): HTML контент страницы продукта.
#         product_url (str): URL страницы продукта.
#
#     Возвращает:
#         tuple: Кортеж с данными продукта, названием, ценой и описанием.
#     """
#     try:
#         soup = BeautifulSoup(html_content, 'html.parser')
#
#         data = {}
#
#         import unicodedata
#
#         # Получаем элемент с названием товара по новому селектору
#         title_element = soup.find('h1', attrs={'data-test-id': 'pdp-title'})
#         raw_name = title_element.text.strip() if title_element else "Название не найдено"
#
#         def is_letter_digit_or_space(char):
#             """
#             Проверяет, является ли символ буквой (любой алфавит Unicode),
#             цифрой или пробелом.
#             """
#             uni_category = unicodedata.category(char)
#             return uni_category.startswith('L') or uni_category.startswith('N') or char.isspace()
#
#         # Очищаем название, оставляя только буквы, цифры и пробелы
#         name = ''.join(char for char in raw_name if is_letter_digit_or_space(char))
#
#         # Убираем лишние пробелы (множественные подряд)
#         name = ' '.join(name.split())
#
#         data['Name'] = name
#
#         # Сохраняем ссылку на товар
#         data['Product urls'] = product_url
#
#         # Получаем блок с ценой по новому селектору
#         price = None
#         price_region = soup.find('div', attrs={'data-test-id': 'pdp-price-region'})
#         if price_region:
#             # Ищем цену со скидкой (актуальную цену)
#             sale_price_span = price_region.find('span', attrs={'data-test-id': 'item-sale-price-pdp'})
#             if sale_price_span and sale_price_span.text.strip():
#                 price_str = sale_price_span.text.strip()
#             else:
#                 # Если нет цены со скидкой, берем обычную цену
#                 price_span = price_region.find('span', attrs={'data-test-id': 'item-price-pdp'})
#                 price_str = price_span.text.strip() if price_span else None
#
#             if price_str:
#                 # Убираем символы валюты и пробелы
#                 price_str_clean = price_str.replace('₹', '').replace(',', '').strip()
#                 try:
#                     price = float(re.sub(r'[^\d.]', '', price_str_clean))
#                 except ValueError:
#                     logging.error(f"Не удалось преобразовать цену в число: {price_str_clean}")
#                     price = None
#
#         data['price'] = price if price is not None else 0.0
#
#         # Описание
#         description = ""
#         product_details_div = soup.find("div", attrs={"data-test-id": "pdp-product-description"})
#
#         if product_details_div:
#             # Ищем заголовок "Description" (в вашем примере это <h2> с текстом "Description")
#             description_h2 = product_details_div.find(
#                 lambda tag: tag.name in ['h2', 'h3'] and tag.get_text(strip=True) == "Description")
#             if description_h2:
#                 # Ищем следующий sibling с текстом описания (обычно div с текстом)
#                 description_div = description_h2.find_next_sibling()
#                 if description_div:
#                     description_text = description_div.get_text(separator="\n", strip=True)
#                     if description_text:
#                         description += description_text + "\n\n"
#
#             # Ищем дополнительные списки с информацией (например, ul с классом, содержащим 'list-disc')
#             additional_lists = product_details_div.find_all('ul', class_=lambda x: x and 'list-disc' in x)
#             for ul in additional_lists:
#                 ul_texts = []
#                 for li in ul.find_all('li'):
#                     li_text = li.get_text(strip=True)
#                     if li_text:
#                         ul_texts.append(f"- {li_text}")
#                 if ul_texts:
#                     description += "Additional Information:\n" + "\n".join(ul_texts) + "\n\n"
#
#         data['descriptions'] = description.strip()
#
#         # Добавляем извлечение additional_description
#         additional_description = ""
#         product_options_wrapper = soup.find('div', class_='product-options-wrapper')
#         if product_options_wrapper:
#             customize_title = product_options_wrapper.find('span', id='customizeTitle')
#             if customize_title:
#                 additional_description += f"Customize: {customize_title.text.strip()}\n"
#
#             bundle_options = product_options_wrapper.find_all('div', class_='field choice')
#             for option in bundle_options:
#                 label = option.find('label', class_='label')
#                 if label:
#                     additional_description += f"- {label.text.strip()}\n"
#
#         data['additional_description'] = additional_description.strip()
#         desc = data['descriptions']
#
#         # Images
#         image_urls = []
#         gallery_section = soup.find('div', class_='tw-vk1bow')
#         if gallery_section:
#             # Ищем все <img> внутри секции галереи
#             img_tags = gallery_section.find_all('img')
#             for img in img_tags:
#                 # Берём src только если он начинается с http (или https)
#                 src = img.get('src')
#                 if src and src.startswith('http'):
#                     image_urls.append(src)
#         data['image_urls'] = image_urls  # Сохраняем все URL изображений
#
#         # Категория и подкатегории
#         breadcrumbs_div = soup.find('div', class_='breadcrumbs')
#         if breadcrumbs_div:
#             breadcrumb_links = breadcrumbs_div.find_all('a', class_='arv')
#             categories = [link.text.strip() for link in breadcrumb_links]
#             data['Category'] = categories[0] if categories else "Категория не определена"
#             data['Subcategory'] = categories[1:] if len(categories) > 1 else []
#         else:
#             data['Category'] = "Категория не определена"
#             data['Subcategory'] = []
#
#         # Производитель
#         data['Brand'] = "Puma"
#
#         # Размер
#         data['Sizes'] = "100 капсул"
#
#         # Доставка
#         shipping_info = []
#         shipping_wrap = soup.find('div', class_='shipping-wrap')
#         if shipping_wrap:
#             shipping_blocks = shipping_wrap.find_all('div', class_='shipping-block')
#             for block in shipping_blocks:
#                 text = block.find('p').text.strip()
#                 shipping_info.append(text)
#         data['Delivery'] = shipping_info if shipping_info else "Информация о доставке не найдена"
#
#         # SKU
#         sku = None
#         more_info_table = soup.find('table', class_='data table additional-attributes')
#         if more_info_table:
#             sku_row = more_info_table.find('tr')
#             if sku_row:
#                 sku_label_cell = sku_row.find('td', class_='col label sku')
#                 sku_data_cell = sku_row.find('td', class_='col data sku')
#                 if sku_label_cell and sku_data_cell:
#                     if sku_label_cell.text.strip() == 'SKU:':
#                         sku = sku_data_cell.text.strip()
#
#         data['SKU'] = sku if sku else "SKU не найден"
#
#         # Рейтинг
#         rating_summary = soup.find('div', class_='rating-summary')
#         if rating_summary:
#             rating_result = rating_summary.find('div', class_='rating-result')
#             if rating_result:
#                 title = rating_result['title']
#                 # Extract the percentage from the title
#                 rating_percentage = title.replace('%', '').strip()
#                 try:
#                     rating = float(rating_percentage)
#                 except ValueError:
#                     rating = 0.0
#                 data['rating'] = str(rating)
#                 print(f"Rating: {rating}")
#             else:
#                 data['rating'] = "0"
#                 print("Rating result not found")
#         else:
#             data['rating'] = "0"
#             print("Rating summary not found")
#
#         return data, name, price, desc
#
#     except Exception as e:
#         logging.error(f"Ошибка при парсинге продукта {product_url}: {e}")
#         return None, None, None, None
#
# def save_product_to_db(data, name, price, desc):
#     try:
#         logging.info(f"Начало сохранения продукта: {name}")
#
#         # Проверка и очистка поля Category
#         category_name = data.get('Category') or "General"
#         category, created = Category.objects.get_or_create(name=category_name)
#
#         # Очищаем название и обрезаем до 100 символов
#         cleaned_name = unidecode.unidecode(name)
#         cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_name).strip()[:100]
#
#         # Проверка и очистка поля SKU
#         sku = data.get('SKU')
#         if not sku or sku.strip().lower() == 'sku не найден':
#             sku = None  # Очистка некорректного значения
#
#         # Генерация базового slug
#         base_slug = slugify(sku)[:500] if sku else slugify(cleaned_name)[:500]
#         slug = generate_unique_slug(base_slug)
#
#         # Проверка и создание бренда
#         brand_name = data.get('Brand') or 'Puma'
#         brand, brand_created = Brand.objects.get_or_create(
#             name=brand_name,
#             defaults={'slug': slugify(brand_name)}
#         )
#
#         # Проверка и обработка изображений
#         image_urls = data.get('image_urls', [])
#         main_image_url = image_urls[0] if image_urls else None
#         main_image_path = download_image(main_image_url, slug) if main_image_url else None
#
#         # Если путь изображения слишком длинный, обрезаем его
#         if main_image_path and len(main_image_path) > 100:
#             main_image_path = main_image_path[:100]
#
#         # Проверка на существование продукта
#         existing_product = Product.objects.filter(slug=slug).first()  # Ищем по slug, или используем sku
#
#         if existing_product:
#             # Если продукт найден, обновляем только цену
#             logging.info(f"Продукт {name} уже существует. Обновляем цену.")
#             existing_product.price = price
#             existing_product.save()
#         else:
#             # Если продукт не найден, создаем новый
#             logging.info(f"Сохраняем новый продукт: {name}")
#             product = Product.objects.create(
#                 slug=slug,
#                 name=cleaned_name,
#                 desc=desc,
#                 price=price,
#                 image=main_image_path,
#                 rating=data.get('rating', '0'),
#                 additional_description=data.get('additional_description', ''),
#                 brand=brand,
#                 sku=sku  # безопасно: None или корректный SKU
#             )
#
#             # Добавление категории
#             product.category.add(category)
#
#         # Добавление дополнительных изображений
#         if len(image_urls) > 1:
#             for img_url in image_urls[1:]:
#                 try:
#                     additional_image_path = download_image(img_url, slug, is_additional=True)
#                     # Если путь изображения слишком длинный, обрезаем его
#                     if additional_image_path and len(additional_image_path) > 100:
#                         additional_image_path = additional_image_path[:100]
#                     if additional_image_path:
#                         if not ProductImage.objects.filter(product=product, image=additional_image_path).exists():
#                             ProductImage.objects.create(product=product, image=additional_image_path)
#                 except Exception as e:
#                     logging.error(f"Ошибка при добавлении изображения: {e}")
#
#         return True
#     except Exception as e:
#         logging.error(f"КРИТИЧЕСКАЯ ОШИБКА при сохранении продукта {name}: {e}", exc_info=True)
#         return False
#
# def collect_all_product_links(category_urls):
#     """
#     Собирает все ссылки на продукты из списка URL категорий.
#
#     Аргументы:
#         category_urls (list): Список URL категорий.
#
#     Возвращает:
#         list: Список всех ссылок на продукты.
#     """
#     all_product_links = set()
#     for url in category_urls:
#         product_links = collect_product_links_from_category(url)
#         all_product_links.update(product_links)
#     return list(all_product_links)
#
# def create_hierarchy(data):
#     for main, subs in data.items():
#         main_cat, created_main = Category.objects.get_or_create(name=main, parent=None)
#         for sub, subsubs in subs.items():
#             sub_cat, created_sub = Category.objects.get_or_create(name=sub, parent=main_cat)
#             for subsub in subsubs:
#                 _, created_subsub = Category.objects.get_or_create(name=subsub, parent=sub_cat)
#                 if created_subsub:
#                     print(f"Создана подкатегория: {subsub} → {sub} → {main}")
#     print("Категории обновлены.")
#
# if __name__ == "__main__":
#     create_hierarchy(CATEGORIES)
#     category_urls = [
#         'https://in.puma.com/in/en/mens',
#
#     ]
#
#     product_links = collect_all_product_links(category_urls)  # Собираем ссылки на продукты
#     print(f"Найдено {len(product_links)} ссылок на продукты.")
#
#     all_products_data = []  # Список для хранения данных о всех продуктах
#     for product_url in product_links:
#         try:
#             response = requests.get(product_url, timeout=10)  # Отправляем GET запрос к URL продукта
#             response.raise_for_status()  # Проверяем статус ответа
#
#             html_content = response.text  # Получаем HTML контент страницы
#
#         except requests.exceptions.RequestException as e:
#             logging.error(f"Не удалось получить {product_url}: {e}")  # Обрабатываем ошибку запроса
#             continue
#
#         product_data, name, price, desc = parse_puma_product(html_content, product_url)  # Парсим данные продукта
#         if product_data:
#             all_products_data.append(product_data)  # Добавляем данные продукта в список
#             print(f"Информация о продукте успешно спарсена с {product_url}")
#             save_product_to_db(product_data, name, price, desc)  # Сохраняем данные продукта в базу данных
#         else:
#             print(f"Не удалось получить информацию о продукте с {product_url}")
#
#     with open('jsons/product_puma.json', 'w', encoding='utf-8') as f:
#         json.dump(all_products_data, f, indent=4, ensure_ascii=False)  # Сохраняем данные в JSON файл
#
#     print("Данные о продуктах сохранены в product_puma.json")
#
#     csv_file = 'jsons/product_puma.csv'
#
#     if all_products_data:
#         # Преобразуем поля с списками в строки без скобок
#         for product in all_products_data:
#             # Обработка поля с ссылками на изображения
#             if isinstance(product.get('image_urls'), list):
#                 product['image_urls'] = ', '.join(product['image_urls'])
#             # Обработка поля подкатегорий (с заглавной буквы)
#             if isinstance(product.get('Subcategory'), list):
#                 product['Subcategory'] = ', '.join(product['Subcategory'])
#             # Обработка поля доставки (с заглавной буквы)
#             if isinstance(product.get('Delivery'), list):
#                 product['Delivery'] = ', '.join(product['Delivery'])
#
#         # Получаем заголовки из ключей первого словаря
#         fieldnames = all_products_data[0].keys()
#
#         with open(csv_file, 'w', newline='', encoding='utf-8') as f_csv:
#             writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
#             writer.writeheader()
#             writer.writerows(all_products_data)
#     else:
#         print("Данные для CSV пусты, файл не создан.")
import time
import json
import os
import django
import csv
import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goabay_bot.settings")
django.setup()

from bot_app.models import Product
from site_app.models import Category, Brand


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import json


def parse_json_ld(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    script_tags = soup.find_all('script', type='application/ld+json')
    products = []
    category_name = None
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

        if typ == 'BreadcrumbList':
            for item in json_data.get('itemListElement', []):
                if item.get('position') == 2:
                    category_name = item.get('name')

        elif typ == 'ProductGroup':
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
                    'category': category_name,
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
                'category': category_name,
                'color': json_data.get('color'),
                'size': '',
                'description': '',
            })

    # Добавляем описание
    description_tag = soup.find('div', {'data-test-id': 'pdp-product-description'})
    description = description_tag.get_text(strip=True) if description_tag else "Описание не найдено"
    for product in products:
        product['description'] = description

    # Парсим размеры
    sizes = []
    for label in soup.select('label[data-size]'):
        size_span = label.select_one('span[data-content="size-value"]')
        if size_span:
            sizes.append(size_span.get_text(strip=True))
    sizes_str = ', '.join(sizes) if sizes else 'Нет в наличии'
    for product in products:
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
        if item.get('category'):
            cat, _ = Category.objects.get_or_create(name=item['category'].strip())
            categories.append(cat)

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
            print(f"🔄 Обновлён продукт: {product.name}")
        else:
            print(f"✅ Создан продукт: {product.name}")

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


if __name__ == '__main__':
    category_urls = [
        'https://in.puma.com/in/en/mens',
    ]

    product_links = collect_all_product_links(category_urls)
    print(f"Найдено {len(product_links)} ссылок на продукты.")

    all_products_data = []
    for product_url in product_links:
        try:
            response = requests.get(product_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
        except requests.RequestException as e:
            print(f"Не удалось получить {product_url}: {e}")
            continue

        products = parse_json_ld(html_content)
        if products:
            all_products_data.extend(products)
            print(f"Информация о продукте успешно спарсена с {product_url}")
        else:
            print(f"Не удалось получить информацию о продукте с {product_url}")

    os.makedirs('jsons', exist_ok=True)

    with open('jsons/product_puma.json', 'w', encoding='utf-8') as f:
        json.dump(all_products_data, f, indent=4, ensure_ascii=False)
    print("✅ JSON сохранён: product_puma.json")

    with open('jsons/product_puma.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'url', 'price', 'currency', 'image', 'brand', 'category', 'color', 'size', 'description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for product in all_products_data:
            if isinstance(product['image'], list):
                product['image'] = product['image'][0]
            writer.writerow(product)
    print("✅ CSV сохранён: product_puma.csv")

    save_to_db(all_products_data)
