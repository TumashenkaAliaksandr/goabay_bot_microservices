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
from bot_app.models import Product, ProductImage  # Импортируем модели
from site_app.models import Brand, Category
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
    """
    try:
        # Извлекаем данные из словаря
        category_name = data['категория'] if data['категория'] else "General"

        # Получаем или создаем категорию
        category, created = Category.objects.get_or_create(name=category_name)

        # Преобразуем не-ASCII символы и создаем слаг
        cleaned_name = unidecode.unidecode(name)
        cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_name).strip()[:100]  # Обрезаем до 100 символов

        # Создаем слаг на основе очищенного названия
        slug = cleaned_name.replace(' ', '-').lower()

        # Получаем название бренда из данных
        brand_name = data.get('производитель') or 'Isha Life'  # Установите значение по умолчанию

        # Получаем или создаем бренд
        brand, brand_created = Brand.objects.get_or_create(
            name=brand_name,
            defaults={'slug': slugify(brand_name)}
        )
        if brand_created:
            logging.info(f"Бренд '{brand_name}' создан и сохранен в базе данных.")
        else:
            logging.info(f"Бренд '{brand_name}' уже существует в базе данных.")

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
                'brand': brand  # Присваиваем экземпляр бренда
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
        # 'https://ishalife.sadhguru.org/in/rudraksha/consecrated-panchamukhi-malas',
        # 'https://ishalife.sadhguru.org/in/rudraksha/consecrated-rudraksha-beads',
        # 'https://ishalife.sadhguru.org/in/yogastore/copper-water-storage',
        # 'https://ishalife.sadhguru.org/in/yogastore/copper-drink-ware/copper-water-bottle',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated/vibhuti',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/temple/adiyogi-miniatures',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/temple',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated/linga-bhairavi-pendant',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated/devi-consecrated-sarees',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated-rudraksha/consecrated-panchamukhi-malas',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated-rudraksha/spatik-malas',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated/devi-abhaya-sutra',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated/dhyanalinga-yantras',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated/snake-ring',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated/jeevarasam',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated/linga-jyothi',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated/dhyanalinga-pendant',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated/pooja-offerings',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated/devi-shawls-vastram',
        # 'https://ishalife.sadhguru.org/in/rudraksha/spatik-malas',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated/linga-bhairavi-gudi',
        # 'https://ishalife.sadhguru.org/in/yogastore',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-mats',
        # 'https://ishalife.sadhguru.org/in/yogastore/copper-drink-ware',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-accessories',
        # 'https://ishalife.sadhguru.org/in/natural-food',
        # 'https://ishalife.sadhguru.org/in/health-immunity',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/save-the-weave',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/men',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/women',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/accessories',
        # 'https://ishalife.sadhguru.org/in/clothing-accessories/save-the-weave/sarees',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/shop-by-fabric',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/shop-by-fabric/organic-cotton',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/shop-by-fabric/cotton',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/shop-by-fabric/undyed',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/shop-by-fabric/handloom',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/shop-by-fabric/bamboo-fibre',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/men/dhoti-pants',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/men/yoga-kurtas',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/men/t-shirts',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/women/dhoti-pants',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/women/kurtas',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/women/t-shirts',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/women/pants',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/women/skirts',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/unisex',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/unisex/dhoti',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/unisex/t-shirt',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/unisex/jackets',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/program-clothing',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/program-clothing/samyama-clothing',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/program-clothing/sadhana-clothing',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/collections',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/collections/adiyogi',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/collections/mystic-moon',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/collections/nandi-collection',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/kids-clothing',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/save-soil',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/accessories/bags',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/accessories/bandanas',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/accessories/purses',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/accessories/stoles-scarves',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/accessories/towel',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/jewellery',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/jewellery/pendants',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/jewellery/earrings',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/jewellery/rings',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/jewellery/bangles',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/jewellery/bracelets-cuffs',
        # 'https://ishalife.sadhguru.org/in/clothings-accessories/jewellery/chains',
        # 'https://ishalife.sadhguru.org/in/bodycare',
        # 'https://ishalife.sadhguru.org/in/bloom',
        # 'https://ishalife.sadhguru.org/in/bodycare/bloom-certified-organic-care/body',
        # 'https://ishalife.sadhguru.org/in/bodycare/bloom-certified-organic-care/body/organic-body-lotions',
        # 'https://ishalife.sadhguru.org/in/bodycare/bloom-certified-organic-care/body/organic-body-wash',
        # 'https://ishalife.sadhguru.org/in/bodycare/bloom-certified-organic-care/hair',
        # 'https://ishalife.sadhguru.org/in/bodycare/bloom-certified-organic-care/hair/organic-hair-shampoos',
        # 'https://ishalife.sadhguru.org/in/bodycare/bloom-certified-organic-care/hair/organic-hair-serums',
        # 'https://ishalife.sadhguru.org/in/bodycare/bloom-certified-organic-care/face',
        # 'https://ishalife.sadhguru.org/in/bodycare/bloom-certified-organic-care/face/organic-face-wash',
        # 'https://ishalife.sadhguru.org/in/bodycare/bloom-certified-organic-care/face/organic-face-serums',
        # 'https://ishalife.sadhguru.org/in/bodycare/100-natural-bodycare',
        # 'https://ishalife.sadhguru.org/in/bodycare/100-natural-bodycare/bath-powder',
        # 'https://ishalife.sadhguru.org/in/bodycare/100-natural-bodycare/shampoo-powder',
        # 'https://ishalife.sadhguru.org/in/bodycare/100-natural-bodycare/face-pack',
        # 'https://ishalife.sadhguru.org/in/bodycare/100-natural-bodycare/pure-coconut-oil',
        # 'https://ishalife.sadhguru.org/in/bodycare/100-natural-bodycare/bath-oil',
        # 'https://ishalife.sadhguru.org/in/bodycare/100-natural-bodycare/hair-oil',
        # 'https://ishalife.sadhguru.org/in/bodycare/100-natural-bodycare/solid-perfume',
        # 'https://ishalife.sadhguru.org/in/bodycare/oral-care',
        # 'https://ishalife.sadhguru.org/in/home/incense-sticks-cones',
        # 'https://ishalife.sadhguru.org/in/home/incense-sticks-cones/incense',
        # 'https://ishalife.sadhguru.org/in/home/incense-sticks-cones/sambarani-dasangam',
        # 'https://ishalife.sadhguru.org/in/home/incense-sticks-cones/cones',
        # 'https://ishalife.sadhguru.org/in/home/fragrance-accessories',
        # 'https://ishalife.sadhguru.org/in/home/fragrance-accessories/incense-stand',
        # 'https://ishalife.sadhguru.org/in/home/fragrance-accessories/burner',
        # 'https://ishalife.sadhguru.org/in/home/fragrance-accessories/fumer',
        # 'https://ishalife.sadhguru.org/in/home/deepam',
        # 'https://ishalife.sadhguru.org/in/home/deepam/lamps-diyas',
        # 'https://ishalife.sadhguru.org/in/home/deepam/devi-dhyanalinga-lamps',
        # 'https://ishalife.sadhguru.org/in/home/deepam/tea-light-holders',
        # 'https://ishalife.sadhguru.org/in/home/urulis',
        # 'https://ishalife.sadhguru.org/in/home/urulis/stone-urulis',
        # 'https://ishalife.sadhguru.org/in/home/urulis/copper-urulis',
        # 'https://ishalife.sadhguru.org/in/home/wall-hangings',
        # 'https://ishalife.sadhguru.org/in/home/wall-hangings/moon-wall-hangings',
        # 'https://ishalife.sadhguru.org/in/home/wall-hangings/shiva-wall-panels',
        # 'https://ishalife.sadhguru.org/in/home/hooks-hangers',
        # 'https://ishalife.sadhguru.org/in/home/stationery',
        # 'https://ishalife.sadhguru.org/in/2025-calendars-diaries',
        # 'https://ishalife.sadhguru.org/in/home/stationery/key-chains',
        # 'https://ishalife.sadhguru.org/in/home/stationery/fridge-magnets',
        # 'https://ishalife.sadhguru.org/in/home/stationery/notepads',
        # 'https://ishalife.sadhguru.org/in/home/stationery/pens',
        # 'https://ishalife.sadhguru.org/in/media/books',
        # 'https://ishalife.sadhguru.org/in/media/books/best-sellers',
        # 'https://ishalife.sadhguru.org/in/media/books/english',
        # 'https://ishalife.sadhguru.org/in/media/books/gujarati',
        # 'https://ishalife.sadhguru.org/in/media/books/hindi',
        # 'https://ishalife.sadhguru.org/in/media/books/kannada',
        # 'https://ishalife.sadhguru.org/in/media/books/malayalam',
        # 'https://ishalife.sadhguru.org/in/media/books/marathi',
        # 'https://ishalife.sadhguru.org/in/media/books/odia',
        # 'https://ishalife.sadhguru.org/in/media/books/tamil',
        # 'https://ishalife.sadhguru.org/in/media/books/telugu',
        # 'https://ishalife.sadhguru.org/in/media/pen-drives',
        # 'https://ishalife.sadhguru.org/in/media/pen-drives/mahabharat',
        # 'https://ishalife.sadhguru.org/in/media/pen-drives/audio-discourses',
        # 'https://ishalife.sadhguru.org/in/media/pen-drives/video-discourses',
        # 'https://ishalife.sadhguru.org/in/sadhguru-chant-box',
        # 'https://ishalife.sadhguru.org/in/media/photos',
        # 'https://ishalife.sadhguru.org/in/media/photos/adiyogi',
        # 'https://ishalife.sadhguru.org/in/media/photos/dhyanalinga',
        # 'https://ishalife.sadhguru.org/in/media/photos/linga-bhairavi',
        # 'https://ishalife.sadhguru.org/in/media/photos/sadhguru',
        # 'https://ishalife.sadhguru.org/in/media/dvds',
        # 'https://ishalife.sadhguru.org/in/media/dvds/in-conversation',
        # 'https://ishalife.sadhguru.org/in/media/dvds/tamil',
        # 'https://ishalife.sadhguru.org/in/media/dvds/english',
        # 'https://ishalife.sadhguru.org/in/media/dvds/yoga',
        # 'https://ishalife.sadhguru.org/in/media/music',
        # 'https://ishalife.sadhguru.org/in/media/music/dhyanalinga',
        # 'https://ishalife.sadhguru.org/in/media/music/sounds-of-isha',
        # 'https://ishalife.sadhguru.org/in/home',
        # 'https://ishalife.sadhguru.org/in/media',
        # 'https://ishalife.sadhguru.org/in/devi-panel',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/temple/devi-yantras-accessories',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/temple/sannidhi-accessories',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/temple/incense-sambrani',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/temple/lamps-diyas',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/temple/pooja-essentials',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/temple/photos',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/temple/chant-box',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/temple/temple-merchandise',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/temple/wall-panels',
        # 'https://ishalife.sadhguru.org/in/temple-consecrated/consecrated-rudraksha/consecrated-rudraksha-beads',
        # 'https://ishalife.sadhguru.org/in/yogastore/copper-drink-ware/copper-glass-tumbler',
        # 'https://ishalife.sadhguru.org/in/yogastore/copper-drink-ware/copper-jug-set',
        # 'https://ishalife.sadhguru.org/in/yogastore/copper-containers',
        # 'https://ishalife.sadhguru.org/in/yogastore/copper-serveware',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-mats/rug-mats',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-mats/natural-straw-mats',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-mats/organic-mats',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-mats/pranayam-cushions',
        # 'https://ishalife.sadhguru.org/in/yogastore/sadhana-essentials',
        # 'https://ishalife.sadhguru.org/in/yogastore/sadhana-essentials/bhuta-shuddhi-kit-refills',
        # 'https://ishalife.sadhguru.org/in/yogastore/sadhana-essentials/sadhana-clothing',
        # 'https://ishalife.sadhguru.org/in/yogastore/sadhana-essentials/shivanga-sadhana',
        # 'https://ishalife.sadhguru.org/in/yogastore/sadhana-essentials/guru-pooja-set',
        # 'https://ishalife.sadhguru.org/in/yogastore/meditation-mats',
        # 'https://ishalife.sadhguru.org/in/yogastore/meditation-mats/cotton-mats',
        # 'https://ishalife.sadhguru.org/in/yogastore/meditation-mats/dharba-grass-mats',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-accessories/mat-covers',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-accessories/bags',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-accessories/purses',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-accessories/towels',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-accessories/eye-pillow-wash-cup',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-accessories/yoga-merchandise',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-clothing',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-clothing/mens',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-clothing/womens',
        # 'https://ishalife.sadhguru.org/in/yogastore/yoga-clothing/stoles-scarves',
        # 'https://ishalife.sadhguru.org/in/yogastore/themes',
        # 'https://ishalife.sadhguru.org/in/yogastore/themes/indian-experience-range',
        # 'https://ishalife.sadhguru.org/in/yogastore/themes/mystical-range',
        # 'https://ishalife.sadhguru.org/in/yogastore/themes/natural-range',
        # 'https://ishalife.sadhguru.org/in/yogastore/themes/organic-range',
        # 'https://ishalife.sadhguru.org/in/natural-food/yogicbites'
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
