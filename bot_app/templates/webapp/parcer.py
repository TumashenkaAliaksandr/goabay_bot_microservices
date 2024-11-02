import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


# Функция для получения данных о продукте по URL
def fetch_product_data(url):
    """Функция для получения данных о продукте по URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на успешный ответ
    except requests.RequestException as e:
        return {"error": f"Ошибка при запросе: {e}"}

    soup = BeautifulSoup(response.content, 'html.parser')

    product_info = {}

    # Получение фотографии
    image_tag = soup.find('div', class_='woocommerce-product-gallery__wrapper').find('img')
    if image_tag:
        product_info['image'] = image_tag.get('src')

    # Получение названия
    title_tag = soup.find('h1', string=lambda x: isinstance(x, str))
    if title_tag:
        product_info['name'] = title_tag.text.strip()

    # Получение описания и ограничение его до 200 символов
    description_tags = soup.select('p')  # Изменено на общий селектор для всех <p>
    descriptions_list = [tag.text.strip() for tag in description_tags]
    full_description = '\n'.join(descriptions_list)

    # Обрезка описания до 200 символов
    if len(full_description) > 200:
        # Найти первую точку в пределах 200 символов
        end_index = full_description[:200].rfind('.')
        if end_index != -1:
            # Обрезать до первой точки
            full_description = full_description[:end_index + 1]
        else:
            # Если точки нет, просто обрезать до 200 символов и добавить троеточие
            full_description = full_description[:200] + '...'

    product_info['description'] = full_description

    # Получение цены
    price_tag = soup.find('span', class_='woocs_price_code')
    if price_tag:
        original_price_tag = price_tag.find('del')
        current_price_tag = price_tag.find('ins')

        original_price = original_price_tag.find('bdi').text if original_price_tag else "Не указана"
        current_price = current_price_tag.find('bdi').text if current_price_tag else "Не указана"

        product_info['price'] = {
            'original': original_price,
            'current': current_price
        }

    return product_info
