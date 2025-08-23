import csv
import json
import os
import random
import string
import time

import django
import requests
from bs4 import BeautifulSoup
from decimal import Decimal
from django.core.files.base import ContentFile
from django.utils.text import slugify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Настройка Django, если требуется сохранение в БД
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goabay_bot.settings")
django.setup()

from bot_app.models import Product, ProductImage, ProductVariant, VariantImage
from site_app.models import Category, Brand


def generate_random_id(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def collect_product_links_with_scroll(category_url, scroll_pause=2, max_scrolls=30):
    """
    Собирает все ссылки товаров на странице категории с динамической подгрузкой (скроллом).
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)

    try:
        driver.get(category_url)
        last_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = 0

        while scrolls < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Достигли конца страницы
            last_height = new_height
            scrolls += 1

        soup = BeautifulSoup(driver.page_source, "html.parser")

        product_links = set()
        # Особенность Biba: ссылки товаров содержат "/product/"
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/product/' in href:
                # создаём полный URL, если нужно
                if href.startswith('/'):
                    full_url = 'https://www.biba.in' + href
                else:
                    full_url = href
                product_links.add(full_url)

        return list(product_links)
    finally:
        driver.quit()


def extract_product_info_and_variations(url):
    """
    Извлекает информацию о товаре с его вариациями с страницы товара Biba.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.product_title')))  # Название товара

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        brand = "Biba"

        # Название продукта
        product_name_tag = soup.find('h1', class_='product_title')
        product_name = product_name_tag.get_text(strip=True) if product_name_tag else "Неизвестное название"

        # Цена
        sale_price = None
        original_price = None

        # На Biba цены часто в span с классом price или ins/del для скидок
        price_div = soup.find('p', class_='price')
        if price_div:
            ins_price = price_div.find('ins')
            del_price = price_div.find('del')
            if ins_price:
                sale_price = ins_price.get_text(strip=True)
                original_price = del_price.get_text(strip=True) if del_price else None
            else:
                # Если нет ins/del, то есть просто span с ценой
                sale_price = price_div.get_text(strip=True)

        # Описание
        description = ""
        desc_div = soup.find('div', class_='woocommerce-product-details__short-description')
        if desc_div:
            description = desc_div.get_text(separator="\n", strip=True)

        # Категории (хлебные крошки). Обычно есть навигация с классом "woocommerce-breadcrumb"
        main_category = ""
        subcategories = ""
        breadcrumb_div = soup.find('nav', class_='woocommerce-breadcrumb')
        if breadcrumb_div:
            crumbs = [a.get_text(strip=True) for a in breadcrumb_div.find_all('a')]
            # Первый - обычно home
            if crumbs and crumbs[0].lower() == 'home':
                crumbs = crumbs[1:]
            if crumbs:
                main_category = crumbs
                if len(crumbs) > 1:
                    subcategories = " / ".join(crumbs[1:])

        # Вариации
        variations = []

        # На biba.in для вариаций цветов и размеров используется select с классом variabla-select,
        # имеющий опции для цветов и размеров
        # Для получения вариаций нужно прочитать select#pa_color и select#pa_size

        # Получим варианты цветов из селекта
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        color_select = soup.find('select', id='pa_color')
        size_select = soup.find('select', id='pa_size')

        colors = []
        if color_select:
            colors = [opt['value'] for opt in color_select.find_all('option') if opt['value'] and opt['value'] != '']
        else:
            colors = ['default_color']

        sizes = []
        if size_select:
            sizes = [opt['value'] for opt in size_select.find_all('option') if opt['value'] and opt['value'] != '']
        else:
            sizes = ['default_size']

        # Главные и дополнительные картинки
        gallery = soup.find('div', class_='woocommerce-product-gallery')
        main_image = None
        all_images = []

        if gallery:
            main_img_tag = gallery.find('img', class_='wp-post-image')
            if main_img_tag and main_img_tag.has_attr('src'):
                main_image = main_img_tag['src']

            # все изображения в галерее
            thumbnails = gallery.find_all('a', class_='woocommerce-gallery__image')
            for thumb in thumbnails:
                href = thumb.get('href')
                if href and href not in all_images:
                    all_images.append(href)

            # добавим главный в all_images, если там нет
            if main_image and main_image not in all_images:
                all_images.insert(0, main_image)

        # Если есть больше одного цвета или размера - считаем variative, иначе simple
        product_type = 'variative' if len(colors) > 1 or len(sizes) > 1 else 'simple'

        # Формируем вариации — каждая вариация цвет+размер, с одними изображениями (Biba редко меняет фото на размер)
        for color in colors:
            # В Biba можно не получить уникальные картинки для каждого цвета без сложного JS
            # Поэтому для простоты назначаем одинаковые изображения для всех цветов
            variation = {
                'color': color,
                'sizes': sizes,
                'main_image': main_image,
                'all_images': all_images,
                'price': sale_price,
                'description': description,
            }
            variations.append(variation)

        product_random_id = generate_random_id()

        product_info = {
            'brand': brand,
            'random_id': product_random_id,
            'product_url': url,
            'product_name': product_name,
            'main_category': main_category,
            'subcategories': subcategories,
            'sale_price': sale_price,
            'original_price': original_price,
            'description': description.replace("\n", " ").strip(),
            'product_type': product_type,
            'variations': variations
        }

        return [product_info]

    except Exception as e:
        print(f"❌ Ошибка при загрузке страницы или поиске элементов: {e}")
    finally:
        driver.quit()

    return []


# Функции для сохранения данных (json и csv)

def save_to_json(data, filename='jsons_files/biba_products.json'):
    if not data:
        print("Нет данных для сохранения.")
        return
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4, ensure_ascii=False)
    print(f"Данные успешно сохранены в файл {filename}")


def save_to_csv(products, filename='csv_files/biba_products.csv'):
    """
    Сохраняет данные товаров с вариациями в CSV для WooCommerce.
    """
    all_colors = set()
    all_sizes = set()
    for product in products:
        for var in product.get('variations', []):
            all_colors.add(var.get('color', ''))
            all_sizes.update(var.get('sizes', []))

    fieldnames = [
        'ID', 'Type', 'SKU', 'Name', 'Parent', 'Brand', 'Product URL', 'Main Category', 'Subcategories',
        'Sale Price', 'Original Price', 'Description', 'Main Image', 'All Images',
        'attribute:Color', 'attribute:Size'
    ]

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for product in products:
            parent_id = product['random_id']
            writer.writerow({
                'ID': parent_id,
                'Type': 'variable',
                'SKU': parent_id,
                'Name': product['product_name'],
                'Parent': '',
                'Brand': product['brand'],
                'Product URL': product['product_url'],
                'Main Category': product['main_category'],
                'Subcategories': product['subcategories'],
                'Sale Price': product['sale_price'],
                'Original Price': product['original_price'],
                'Description': product['description'],
                'Main Image': '',
                'All Images': '',
                'attribute:Color': ', '.join(sorted(all_colors)),
                'attribute:Size': ', '.join(sorted(all_sizes)),
            })

            for var in product.get('variations', []):
                for size in var.get('sizes', []):
                    sku = f"{parent_id}-{var.get('color', '')}-{size}".replace(' ', '').replace('/', '')
                    writer.writerow({
                        'ID': '',
                        'Type': 'variation',
                        'SKU': sku[:100],
                        'Name': '',
                        'Parent': parent_id,
                        'Brand': '',
                        'Product URL': product['product_url'],
                        'Main Category': '',
                        'Subcategories': '',
                        'Sale Price': product['sale_price'],
                        'Original Price': product['original_price'],
                        'Description': '',
                        'Main Image': var.get('main_image', ''),
                        'All Images': ','.join(var.get('all_images', [])),
                        'attribute:Color': var.get('color', ''),
                        'attribute:Size': size,
                    })

    print(f"CSV для WooCommerce успешно сохранён: {filename}")


# Функции для сохранения в Django DB (если нужно)

def save_image_from_url(instance, field_name, url):
    try:
        if not url:
            return
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        file_name = os.path.basename(url.split("?")[0])
        getattr(instance, field_name).save(file_name, ContentFile(response.content), save=True)
        print(f"📸 Изображение сохранено: {file_name}")
    except Exception as e:
        print(f"❌ Ошибка при загрузке изображения {url}: {e}")


def save_parsed_product_to_db(parsed_product, brand_name='Biba'):
    print("\n🔧 Начинаем сохранение товара...")

    parent = None
    main_category = parsed_product.get('main_category', '')
    subcategories = parsed_product.get('subcategories', '')

    cats = []
    if main_category.strip():
        cats.append(main_category.strip())
    if subcategories.strip():
        cats.extend([c.strip() for c in subcategories.split('/') if c.strip()])

    if not cats:
        cats = ['Uncategorized']
        print(f"⚠️ Для товара '{parsed_product.get('product_name', 'Без имени')}' не найдены категории, сохранено в 'Uncategorized'")

    main_cat, *subcats = cats
    for cat_name in [main_cat] + subcats:
        parent, _ = Category.objects.get_or_create(name=cat_name, parent=parent)
    category = parent
    print(f"📂 Категория: {category.name}")

    brand_slug = slugify(brand_name)
    brand, created = Brand.objects.get_or_create(
        slug=brand_slug,
        defaults={'name': brand_name}
    )
    if created:
        print(f"🆕 Создан новый бренд: {brand_name}")
    else:
        print(f"🔄 Найден бренд: {brand_name}")

    base_slug = slugify(parsed_product['product_name'])
    product_slug = base_slug[:500]
    print(f"🆔 Slug продукта: {product_slug}")

    try:
        product = Product.objects.get(slug=product_slug)
        print("🔄 Продукт найден, обновляем данные...")

        updated = False
        if product.name != parsed_product['product_name']:
            product.name = parsed_product['product_name']
            updated = True
        if product.desc != parsed_product.get('description', ''):
            product.desc = parsed_product.get('description', '')
            updated = True
        if product.brand != brand:
            product.brand = brand
            updated = True
        try:
            new_price = Decimal(str(parsed_product.get('sale_price', '')).replace('₹', '').replace(',', '').strip()) if parsed_product.get('sale_price') else None
            if product.price != new_price:
                product.price = new_price
                updated = True
        except:
            pass
        try:
            new_discount = Decimal(str(parsed_product.get('original_price', '')).replace('₹', '').replace(',', '').strip()) if parsed_product.get('original_price') else None
            if product.discount != new_discount:
                product.discount = new_discount
                updated = True
        except:
            pass
        if updated:
            product.save()
            print("🔄 Продукт обновлён")

    except Product.DoesNotExist:
        print("🆕 Продукт не найден, создаём новый...")
        product = Product.objects.create(
            slug=product_slug,
            name=parsed_product['product_name'],
            desc=parsed_product.get('description', ''),
            brand=brand,
            price=None,
            discount=None
        )
        print("✅ Продукт создан")

    if not product.category.filter(id=category.id).exists():
        product.category.add(category)
        print(f"📁 Категория добавлена: {category.name}")

    variations = parsed_product.get('variations', [])
    main_img_url = variations[0].get('main_image') if variations else None
    if main_img_url and (not product.image or not product.image.name):
        save_image_from_url(product, 'image', main_img_url)

    all_variant_images = set()
    for var in variations:
        main_img = var.get('main_image')
        if main_img:
            all_variant_images.add(main_img)

    all_images = {img for var in variations for img in var.get('all_images', [])}
    all_images.update(all_variant_images)

    for img_url in all_images:
        if img_url:
            exists = ProductImage.objects.filter(product=product, image=img_url).exists()
            if not exists:
                img_instance = ProductImage(product=product)
                save_image_from_url(img_instance, 'image', img_url)
                img_instance.save()

    for var in variations:
        color = (var.get('color') or '').strip()[:255]
        sizes = var.get('sizes', []) or ['']
        main_image_url = var.get('main_image')
        try:
            price_var = Decimal(str(var.get('price')).replace('₹', '').replace(',', '').strip()) if var.get('price') else product.price
        except:
            price_var = product.price
        desc_var = var.get('description', '') or parsed_product.get('description', '')

        sku = f"{product_slug}-{color.replace(' ', '').replace('/', '')}"[:100]

        variant_obj, created = ProductVariant.objects.get_or_create(
            product=product,
            color=color,
            defaults={
                'size': sizes,
                'sku': sku,
                'price': price_var,
            }
        )
        if not created:
            updated = False
            if set(variant_obj.size) != set(sizes):
                variant_obj.size = sizes
                updated = True
            if variant_obj.price != price_var:
                variant_obj.price = price_var
                updated = True
            if variant_obj.description != desc_var:
                variant_obj.description = desc_var
                updated = True
            if updated:
                variant_obj.save()
                print(f"🔄 Вариация обновлена: color={color}")

        if main_image_url and (not variant_obj.image or not variant_obj.image.name):
            save_image_from_url(variant_obj, 'image', main_image_url)

        for img_url in var.get('all_images', []):
            if img_url and not variant_obj.additional_images.filter(image=img_url).exists():
                img_instance = VariantImage(variant=variant_obj)
                save_image_from_url(img_instance, 'image', img_url)
                img_instance.save()

        print(f"{'✅' if created else '🔄'} Вариация: color={color}, sizes={sizes}, sku={sku}")

    print(f"\n✅ Продукт сохранён: {product.name}\n")


if __name__ == "__main__":
    # Пример парсинга категории, можно добавить другие категории страниц Biba
    MAIN_CATEGORIES = [
        "https://www.biba.in/intl/ethnic-wear-indian-kurtis.html",
        # другие категории при необходимости...
    ]

    all_product_links = set()
    for cat_url in MAIN_CATEGORIES:
        print(f"Собираем ссылки с категории: {cat_url}")
        links = collect_product_links_with_scroll(cat_url)
        print(f"Найдено товаров: {len(links)}")
        all_product_links.update(links)

    print(f"Всего найдено товаров для парсинга: {len(all_product_links)}")

    all_products = []
    for url in all_product_links:
        print(f"Парсим товар: {url}")
        products = extract_product_info_and_variations(url)
        all_products.extend(products)

    print(f"Всего успешно спарсено товаров: {len(all_products)}")

    save_to_csv(all_products)
    save_to_json(all_products)

    # Раскомментируйте, если хотите сохранять в базу Django
    # for product_data in all_products:
    #     save_parsed_product_to_db(product_data)
