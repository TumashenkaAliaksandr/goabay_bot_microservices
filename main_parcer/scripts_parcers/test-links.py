# # -*- coding: utf-8 -*-
# import csv
# import logging
# import os
# import json
# import re
# import time
# import django
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urlparse
# from django.utils.text import slugify
# from django.core.files.base import ContentFile
#
# from main_parcer.scripts_parcers.categories import CATEGORIES
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "goabay_bot.settings")
# django.setup()
#
# from bot_app.models import Product, ProductVariant, ProductImage
# from site_app.models import Category, Brand
#
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
#
# BASE_URL = "https://in.puma.com"
# MAIN_CATEGORIES = [
#     'https://in.puma.com/in/en/rcb-launch',
# ]
#
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
#
#
#
# def extract_sizes_with_selenium(url):
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#
#
#     driver = webdriver.Chrome(options=options)
#     driver.get(url)
#     time.sleep(3)  # Ждем загрузки страницы (можно увеличить, если надо)
#
#     # Получаем исходный код страницы
#     html = driver.page_source
#
#     # Используем BeautifulSoup для парсинга страницы
#     soup = BeautifulSoup(html, 'html.parser')
#
#     # Пример: ищем все элементы с размерами (например, через data-content)
#     # Подставьте соответствующий класс или аттрибут для размеров
#     size_elements = soup.find_all('span', {'data-content': 'size-value'})
#
#     if size_elements:
#         sizes = [size.get_text(strip=True) for size in size_elements]
#         print(f"✅ Все доступные размеры: {sizes}")
#         driver.quit()
#         return sizes
#     else:
#         print("❌ Размеры не найдены на странице")
#         driver.quit()
#         return None
#
#
# def collect_product_links_from_category(category_url, scroll_pause=2, max_wait_scrolls=300):
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#
#     driver = webdriver.Chrome(options=options)
#     driver.set_page_load_timeout(180)
#     driver.set_script_timeout(180)
#
#     try:
#         driver.get(category_url)
#     except Exception as e:
#         print(f"❌ Ошибка загрузки страницы {category_url}: {e}")
#         driver.quit()
#         return []
#
#     product_links = set()
#     last_links_count = 0
#     wait_counter = 0
#
#     while wait_counter < max_wait_scrolls:
#         try:
#             driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
#             time.sleep(scroll_pause)
#
#             script_tags = driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')
#             for tag in script_tags:
#                 try:
#                     content = tag.get_attribute('innerHTML')
#                     data = json.loads(content)
#                     if data.get('@type') == 'ItemList':
#                         for item in data.get('itemListElement', []):
#                             url = item.get('item', {}).get('url')
#                             if url:
#                                 product_links.add(url)
#                 except:
#                     continue
#
#             if len(product_links) == last_links_count:
#                 break
#             last_links_count = len(product_links)
#             wait_counter += 1
#         except Exception as e:
#             print(f"⚠️ Ошибка при прокрутке: {e}")
#             break
#
#     driver.quit()
#     return list(product_links)
#
#
# def extract_sizes_from_html(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     # Используем map для извлечения всех размеров
#     sizes = list(map(lambda x: x.get_text(strip=True), soup.find_all('span', {'data-content': 'size-value'})))
#
#     return sizes if sizes else ['Нет в наличии']
#
#
# def parse_json_ld(html_content, main_cat, sub_cat):
#     soup = BeautifulSoup(html_content, 'html.parser')
#
#     next_data_script = soup.find('script', id='__NEXT_DATA__')
#     if next_data_script:
#         try:
#             data = json.loads(next_data_script.string)
#             next_data_products = parse_next_data_json(data, soup, main_cat, sub_cat)
#             if next_data_products:
#                 return next_data_products
#         except Exception as e:
#             print(f"⚠️ Ошибка парсинга __NEXT_DATA__: {e}")
#
#     return parse_json_ld_fallback(soup, main_cat, sub_cat)
#
#
# def extract_variant_info_from_insider(html):
#     """
#     Ищет в html скрипт с window.insider_object.product и извлекает color и size.
#     Возвращает dict с ключами 'color' и 'size' или пустой dict, если не найдено.
#     """
#     pattern = re.compile(r'window\.insider_object\.product\s*=\s*({.*?});', re.DOTALL)
#     match = pattern.search(html)
#     if not match:
#         return {}
#
#     try:
#         product_json_str = match.group(1)
#         # Иногда в JSON могут быть одинарные кавычки или невалидные символы, но обычно это валидный JS-объект
#         # Для безопасности можно заменить одинарные кавычки на двойные, если нужно:
#         # product_json_str = product_json_str.replace("'", '"')
#         product_data = json.loads(product_json_str)
#         return {
#             'color': product_data.get('color'),
#             'size': product_data.get('size')
#         }
#     except Exception as e:
#         print(f"⚠️ Ошибка парсинга insider_object.product: {e}")
#         return {}
#
#
# def parse_next_data_json(data, soup, main_cat, sub_cat):
#     products = []
#     try:
#         product = data['props']['pageProps'].get('product', {})
#         variants = product.get('variants', [])
#         base_name = product.get("name")
#         description_tag = soup.find('div', {'data-test-id': 'pdp-product-description'})
#         description = description_tag.get_text(strip=True) if description_tag else product.get('description', '')
#         html = str(soup)
#
#         for variant in variants:
#             image = variant.get("image", {}).get("url") or None
#             price = variant.get("price", {}).get("value")
#             currency = variant.get("price", {}).get("currency")
#
#             variant_url = variant.get("url")
#             insider_info = {}
#             sizes_str = 'Нет в наличии'
#             variant_html = ''
#
#             try:
#                 if variant_url:
#                     full_url = BASE_URL + variant_url if variant_url.startswith('/') else variant_url
#                     variant_resp = requests.get(full_url, timeout=10)
#                     if variant_resp.status_code == 200:
#                         variant_html = variant_resp.text
#                         insider_info = extract_variant_info_from_insider(variant_html)
#                         sizes_list = extract_sizes_from_html(variant_html)
#                         sizes_str = ', '.join(sizes_list)
#                 else:
#                     fallback_url = product.get("url") or product.get("pdpUrl") or ""
#                     if fallback_url:
#                         if not fallback_url.startswith("http"):
#                             fallback_url = BASE_URL + fallback_url
#                         sizes_list = extract_sizes_with_selenium(fallback_url)
#                         sizes_str = ', '.join(sizes_list)
#             except Exception as e:
#                 print(f"⚠️ Ошибка получения размеров вариации: {e}")
#
#             color = variant.get("color") or insider_info.get('color')
#             size = sizes_str
#
#             products.append({
#                 "base_name": base_name,
#                 "variant_name": variant.get("name"),
#                 "url": BASE_URL + variant_url if variant_url else None,
#                 "price": price,
#                 "currency": currency,
#                 "image": image,
#                 "brand": product.get("brand", {}).get("name", "PUMA"),
#                 "category": main_cat,
#                 "subcategory": sub_cat,
#                 "color": color,
#                 "size": size,
#                 "description": description,
#                 "html": variant_html
#             })
#
#     except Exception as e:
#         print(f"⚠️ Ошибка разбора данных из __NEXT_DATA__: {e}")
#
#     return products
#
#
# def parse_json_ld_fallback(soup, main_cat, sub_cat):
#     script_tags = soup.find_all('script', type='application/ld+json')
#     description_tag = soup.find('div', {'data-test-id': 'pdp-product-description'})
#     description = description_tag.get_text(strip=True) if description_tag else "Описание не найдено"
#
#     products = []
#     for tag in script_tags:
#         try:
#             data = json.loads(tag.string)
#         except:
#             continue
#
#         if data.get('@type') == 'ProductGroup':
#             brand = data.get('brand', {}).get('name')
#             product_name = data.get('name')
#
#             for var in data.get('hasVariant', []):
#                 variant_url = BASE_URL + var.get('url', '') if var.get('url') else None
#                 sizes_str = 'Нет в наличии'
#                 html = ''
#
#                 if variant_url:
#                     try:
#                         resp = requests.get(variant_url, timeout=10)
#                         if resp.status_code == 200:
#                             html = resp.text
#                             sizes_str = extract_sizes_from_html(html)
#                     except:
#                         pass
#
#                 products.append({
#                     'base_name': product_name,
#                     'variant_name': var.get('name'),
#                     'url': variant_url,
#                     'price': var.get('offers', {}).get('price'),
#                     'currency': var.get('offers', {}).get('priceCurrency'),
#                     'image': var.get('image'),
#                     'brand': brand,
#                     'category': main_cat,
#                     'subcategory': sub_cat,
#                     'color': var.get('color'),
#                     'size': sizes_str,
#                     'description': description,
#                     'html': html
#                 })
#
#     return products
#
#
# def find_category_path(main_cat, sub_cat):
#     for top, subs in CATEGORIES.items():
#         for mid, leafs in subs.items():
#             for leaf in leafs:
#                 if leaf.lower() in sub_cat.lower():
#                     return [top, mid, leaf]
#             if sub_cat.lower() in mid.lower():
#                 return [top, mid]
#         if sub_cat.lower() in top.lower():
#             return [top]
#     return [main_cat, sub_cat] if main_cat and sub_cat else [main_cat or sub_cat]
#
#
# def get_or_create_category_from_path(path):
#     parent = None
#     for name in path:
#         if not name:
#             continue
#         obj, _ = Category.objects.get_or_create(name=name, parent=parent)
#         parent = obj
#     return parent
#
#
# def save_to_db(products):
#     grouped = {}
#     for item in products:
#         key = slugify(item['base_name'])
#         grouped.setdefault(key, []).append(item)
#
#     json_data = []
#     csv_rows = []
#
#     for slug, variants in grouped.items():
#         base = variants[0]
#
#         if base.get('html') and (not base.get('size') or base.get('size') == 'Нет в наличии'):
#             base['size'] = extract_sizes_from_html(base['html'])
#
#         brand = None
#         if base.get('brand'):
#             brand_slug = slugify(base['brand'])
#             brand, _ = Brand.objects.get_or_create(name=base['brand'], slug=brand_slug)
#
#         cat_path = find_category_path(base['category'], base['subcategory'])
#         cat_obj = get_or_create_category_from_path(cat_path)
#
#         product, created = Product.objects.get_or_create(slug=slug, defaults={
#             'name': base['base_name'],
#             'brand': brand,
#             'desc': base.get('description', ''),
#             'price': base.get('price') or 0,
#             'color': base.get('color', ''),
#             'sizes': base.get('size', ''),
#             'stock_status': 'in_stock'
#         })
#
#         if not created:
#             product.name = base['base_name']
#             product.brand = brand
#             product.desc = base.get('description', '')
#             product.price = base.get('price') or 0
#             product.color = base.get('color', '')
#             product.sizes = base.get('size', '')
#             product.stock_status = 'in_stock'
#             product.save()
#
#         if cat_obj:
#             product.category.set([cat_obj])
#
#         main_image_url = base.get('image')
#         if main_image_url:
#             if isinstance(main_image_url, list):
#                 main_image_url = main_image_url[0]
#             try:
#                 img_data = requests.get(main_image_url).content
#                 product.image.save(main_image_url.split("/")[-1], ContentFile(img_data), save=True)
#             except Exception as e:
#                 print(f"⚠️ Ошибка загрузки главного изображения: {e}")
#
#         for img_url in base.get('additional_images', []):
#             try:
#                 img_data = requests.get(img_url).content
#                 ProductImage.objects.create(
#                     product=product,
#                     image=ContentFile(img_data, name=img_url.split("/")[-1])
#                 )
#             except Exception as e:
#                 print(f"⚠️ Ошибка загрузки дополнительного изображения: {e}")
#
#         for var in variants:
#             if var.get('html') and (not var.get('size') or var.get('size') == 'Нет в наличии'):
#                 var['size'] = extract_sizes_from_html(var['html'])
#
#             sku = slugify(var['variant_name'])[:100]
#             variant_obj, created = ProductVariant.objects.get_or_create(
#                 sku=sku,
#                 defaults={
#                     'product': product,
#                     'color': var.get('color'),
#                     'size': var.get('size')[:50],
#                     'price': var.get('price') or 0,
#                     'quantity': 0,
#                     'description': var.get('description', '')
#                 }
#             )
#
#             if not created:
#                 variant_obj.color = var.get('color')
#                 variant_obj.size = var.get('size')[:50]
#                 variant_obj.price = var.get('price') or 0
#                 variant_obj.description = var.get('description', '')
#                 variant_obj.save()
#
#             image_url = var.get('image')
#             if image_url:
#                 if isinstance(image_url, list):
#                     image_url = image_url[0]
#                 try:
#                     img_data = requests.get(image_url).content
#                     variant_obj.image.save(image_url.split("/")[-1], ContentFile(img_data), save=True)
#                 except Exception as e:
#                     print(f"⚠️ Ошибка загрузки изображения вариации: {e}")
#
#             csv_rows.append({
#                 'product_name': product.name,
#                 'brand': brand.name if brand else '',
#                 'price': var.get('price') or 0,
#                 'category': cat_obj.name if cat_obj else '',
#                 'color': var.get('color'),
#                 'size': var.get('size'),
#                 'sku': sku,
#                 'description': var.get('description', ''),
#                 'image': image_url
#             })
#
#         json_data.append({
#             'name': product.name,
#             'slug': product.slug,
#             'brand': brand.name if brand else '',
#             'desc': product.desc,
#             'price': product.price,
#             'color': product.color,
#             'sizes': product.sizes,
#             'image': main_image_url,
#             'category': cat_path,
#             'variants': variants
#         })
#
#         print(f"✅ Сохранён продукт: {product.name}")
#
#     os.makedirs('jsons', exist_ok=True)
#
#     with open('jsons/products_data.json', 'w', encoding='utf-8') as jf:
#         json.dump(json_data, jf, ensure_ascii=False, indent=4)
#
#     with open('jsons/products_data.csv', 'w', newline='', encoding='utf-8') as cf:
#         fieldnames = ['product_name', 'brand', 'price', 'category', 'color', 'size', 'sku', 'description', 'image']
#         writer = csv.DictWriter(cf, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(csv_rows)
#
#     print("📦 Данные успешно сохранены в JSON и CSV")
#
#
# if __name__ == '__main__':
#     all_products = []
#
#     for category_url in MAIN_CATEGORIES:
#         print(f"\n▶ Обработка категории: {category_url}")
#         links = collect_product_links_from_category(category_url)
#         print(f"  ➤ Найдено ссылок: {len(links)}")
#
#         parsed = urlparse(category_url).path.strip('/').split('/')
#         main_cat = parsed[2] if len(parsed) > 2 else 'unknown'
#         sub_cat = parsed[-1]
#
#         for url in links:
#             try:
#                 r = requests.get(url, timeout=30)
#                 r.raise_for_status()
#                 products = parse_json_ld(r.text, main_cat, sub_cat)
#                 all_products.extend(products)
#                 print(f"  ➕ {url} ({len(products)} вариаций)")
#             except Exception as e:
#                 print(f"❌ Ошибка парсинга {url}: {e}")
#
#     save_to_db(all_products)
#     print(f"\n✅ Парсинг завершён. Всего товаров: {len(all_products)}")


# -------------------
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import time
# from bs4 import BeautifulSoup
#
# # Настройки для запуска браузера без UI (headless режим)
# options = Options()
# options.add_argument("--headless")  # Для запуска без UI
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
#
# # Путь к драйверу Chrome (установите по своему пути)
# driver = webdriver.Chrome(options=options)
#
# def extract_sizes_from_page(url):
#     driver.get(url)
#     time.sleep(3)  # Ждем загрузки страницы (можно увеличить, если надо)
#
#     # Получаем исходный код страницы
#     html = driver.page_source
#
#     # Используем BeautifulSoup для парсинга страницы
#     soup = BeautifulSoup(html, 'html.parser')
#
#     # Пример: ищем все элементы с размерами (например, через data-content)
#     # Подставьте соответствующий класс или аттрибут для размеров
#     size_elements = soup.find_all('span', {'data-content': 'size-value'})
#
#     if size_elements:
#         sizes = [size.get_text(strip=True) for size in size_elements]
#         print(f"✅ Все доступные размеры: {sizes}")
#         driver.quit()
#         return sizes
#     else:
#         print("❌ Размеры не найдены на странице")
#         driver.quit()
#         return None
#
# # Пример использования
# url = "https://in.puma.com/in/en/pd/court-shatter-low-sneakers/399844?size=0240&swatch=04"
# sizes = extract_sizes_from_page(url)
#
# if sizes:
#     print(f"✅ Все размеры: {sizes}")
# else:
#     print("⛔ Не удалось извлечь размеры.")


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

def extract_sizes_for_all_colors(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)  # Увеличиваем размер окна

    wait = WebDriverWait(driver, 15)
    all_data = {}

    try:
        driver.get(url)

        # Ждем загрузки блока с вариантами цвета
        wait.until(EC.presence_of_element_located((By.ID, 'style-picker')))

        # Находим все варианты цвета
        color_variants = driver.find_elements(By.CSS_SELECTOR, '#style-picker label[data-test-id="color"]')

        for idx, color_variant in enumerate(color_variants):
            try:
                color_name = color_variant.find_element(By.CSS_SELECTOR, 'span.sr-only').text.strip()
                if not color_name:
                    color_name = f"color_{idx+1}"

                driver.execute_script("arguments[0].scrollIntoView(true);", color_variant)

                # Ждем, пока элемент станет кликабельным
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'#style-picker label[data-test-id="color"]:nth-child({idx+1})')))

                try:
                    color_variant.click()
                except Exception:
                    # Если обычный клик не сработал — клик через JS
                    driver.execute_script("arguments[0].click();", color_variant)

                # Ждем обновления размеров
                time.sleep(2)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'label[data-size] span[data-content="size-value"]')))

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                size_elements = soup.select('label[data-size] span[data-content="size-value"]')
                sizes = [size.get_text(strip=True) for size in size_elements if size.get_text(strip=True)]

                if not sizes:
                    sizes = ['Нет в наличии']

                all_data[color_name] = sizes
                print(f"✅ Цвет '{color_name}': размеры {sizes}")

            except Exception as e:
                print(f"❌ Ошибка при обработке цвета '{color_name}': {e}")

    except Exception as e:
        print(f"❌ Ошибка при загрузке страницы или поиске элементов: {e}")

    finally:
        driver.quit()

    return all_data

# Пример использования
if __name__ == "__main__":
    url = "https://in.puma.com/in/en/pd/court-shatter-low-sneakers/399844?size=0200&swatch=04"
    sizes_by_color = extract_sizes_for_all_colors(url)

    print("\nВсе размеры по цветам:")
    for color, sizes in sizes_by_color.items():
        print(f"{color}: {sizes}")
