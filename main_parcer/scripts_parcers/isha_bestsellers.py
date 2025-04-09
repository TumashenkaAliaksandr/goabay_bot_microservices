import os
import django

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "goabay_bot.settings")  # Убедись, что указал правильный путь к настройкам

# Инициализация Django
django.setup()

import requests
import json
from bs4 import BeautifulSoup
from site_app.models import Product, Category
import re
from django.utils.text import slugify
from django.core.files.base import ContentFile

# Папка для сохранения изображений
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../media')

def download_image(url, product_name):
    """
    Загружает изображение по URL и сохраняет его локально.
    Возвращает путь к сохраненному изображению.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Получаем имя файла из URL
        filename = url.split("/")[-1].split('?')[0]  # Удаляем параметры после вопросительного знака

        # Очищаем имя продукта для использования в имени файла
        product_name = slugify(product_name)

        # Создаем путь для сохранения изображения
        filepath = os.path.join('products', f'{product_name}_{filename}')

        # Создаем папку для медиафайлов, если она не существует
        media_dir = os.path.join(MEDIA_ROOT, 'products')
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)

        # Сохраняем изображение локально
        if response.status_code == 200:
            with open(os.path.join(MEDIA_ROOT, filepath), 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return filepath
        else:
            print(f"Ошибка при загрузке изображения: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка при загрузке и сохранении изображения: {e}")
        return None


def scrape_bestsellers(url):
    """
    Парсит блок "Yogic Best Sellers" с сайта ishalife.sadhguru.org и сохраняет товары в базу данных.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Находим блок "Yogic Best Sellers"
        bestsellers_section = soup.find('div', class_='home-slider')

        if not bestsellers_section:
            print("Блок 'Yogic Best Sellers' не найден на странице.")
            return []

        # Извлекаем информацию о каждом товаре
        product_items = bestsellers_section.find_all('li', class_='product-item')
        products = []

        for item in product_items:
            name = item.find('strong', class_='product-item-name').text.strip()
            link = item.find('a', class_='product-item-link')['href']
            image_url = item.find('img', class_='product-image-photo')['src']
            price_str = item.find('span', class_='price').text.strip()

            # Очистка цены от символов
            price_str = re.sub(r'[^\d.,]', '',
                               price_str)  # Убираем все ненужные символы, оставляем только цифры и запятую/точку
            price_str = price_str.replace(',', '')  # Убираем запятые, если они присутствуют
            try:
                price = float(price_str)  # Преобразуем цену в число
            except ValueError:
                price = 0.0  # Если не удалось преобразовать, ставим цену 0.0

            # Обработка рейтинга
            try:
                rating_element = item.find('div', class_='rating-result')
                rating_title = rating_element['title']  # Извлекаем процентный рейтинг из атрибута title
                rating_percentage = float(rating_title.replace('%', '').strip())  # Извлекаем только число и проценты
                rating = rating_percentage  # Сохраняем рейтинг как процент
            except:
                rating = "Рейтинг отсутствует"

            # Проверка наличия категории и создание/поиск категории
            category_name = "Yogic"  # Здесь можно использовать логику для поиска категории
            category, created = Category.objects.get_or_create(name=category_name)

            # Загружаем изображение и получаем путь к нему
            image_path = download_image(image_url, name)

            # Обновление или создание товара с уникальным slug
            cleaned_name = re.sub(r'[\(\)\.\-]', ' ', name).strip()
            cleaned_name = re.sub(r'[^\w\s]', '', cleaned_name)
            slug = cleaned_name.replace(' ', '-').lower()

            # Удаляем старое изображение, если оно существует
            try:
                old_product = Product.objects.get(slug=slug)
                if old_product.image:
                    image_path_to_remove = os.path.join(MEDIA_ROOT, old_product.image.path)
                    if os.path.exists(image_path_to_remove):
                        os.remove(image_path_to_remove)
            except Product.DoesNotExist:
                pass

            product, created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'image': image_path,  # Сохраняем путь к локальному изображению
                    'desc': "Описание товара",  # Добавь реальное описание, если оно доступно
                    'price': price,
                    'rating': str(rating),  # Сохраняем рейтинг в базе данных
                }
            )

            # Добавляем категорию через add() для ManyToManyField
            product.category.clear()  # Очищаем существующие категории
            product.category.add(category)

            # Добавляем в список
            products.append({
                'name': name,
                'link': link,
                'image': image_url,
                'price': price,
                'rating': rating  # Рейтинг сохраняется как процент
            })

        return products

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к сайту: {e}")
        return []
    except Exception as e:
        print(f"Произошла ошибка при парсинге: {e}")
        return []


# Пример использования
if __name__ == '__main__':
    url = 'https://ishalife.sadhguru.org/'
    bestsellers = scrape_bestsellers(url)

    if bestsellers:
        print("Бестселлеры Yogic:")
        for product in bestsellers:
            print(f"  Название: {product['name']}")
            print(f"  Ссылка: {product['link']}")
            print(f"  Изображение: {product['image']}")
            print(f"  Цена: {product['price']}")
            print(f"  Рейтинг: {product['rating']}%")  # Рейтинг в процентах
            print("-" * 30)

        # Сохраняем данные в JSON-файл
        with open('jsons/isha_bestsellers_products.json', 'w', encoding='utf-8') as f:
            json.dump(bestsellers, f, ensure_ascii=False, indent=4)
    else:
        print("Не удалось получить бестселлеры.")
