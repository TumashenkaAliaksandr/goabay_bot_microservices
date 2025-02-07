import json
import requests
from bs4 import BeautifulSoup

def parse_product(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        data = {}

        # Основной блок с информацией о продукте
        product_detail = soup.find('div', class_='paprodict-detail')

        if not product_detail:
            print(f"Не удалось найти 'paprodict-detail' на странице {url}")
            return None

        # Название
        title_element = product_detail.find('h1')
        data['название'] = title_element.text.strip() if title_element else "Название не найдено"

        # Ссылка на товар
        data['ссылка на товар'] = url

        # Цена
        price_element = product_detail.find('div', class_='paprice').find('h4')
        data['цена'] = price_element.text.split('MRP:')[0].replace('₹','').strip() if price_element else "Цена не найдена"

        # Описание
        description_meta = product_detail.find('meta', attrs={'property': 'og:description'})
        data['описание'] = description_meta['content'].strip() if description_meta else "Описание не найдено"

        # Фото
        image_meta = product_detail.find('meta', attrs={'property': 'og:image'})
        data['фото'] = image_meta['content'] if image_meta else "Фото не найдено"

        # Категория
        category_parts = url.split('/')
        data['категория'] = category_parts[5] if len(category_parts) > 5 else "Категория не определена"

        # Производитель
        data['производитель'] = "Patanjali"

        # Состав (из Key Ingredients)
        key_ingredients_div = product_detail.find('div', class_='accordion-body')
        data['состав'] = key_ingredients_div.text.strip() if key_ingredients_div else "Состав не указан"

        # Размер
        pavalue_div = product_detail.find('div', class_='pavalue')
        if pavalue_div:
            label = pavalue_div.find('label')
            data['размер'] = label.text.strip() if label else "Не указан"
        else:
            data['размер'] = "Не указан"

        # By combo
        data['by combo'] = "Нет"  # В предоставленном HTML отсутствует

        return data

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе {url}: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")
        return None

# Пример использования с указанным URL
product_url = "https://www.patanjaliayurved.net/product/paridhan/women-ethnic/saree-pwewsrwbro1843008-pink-green/3697"
product_data = parse_product(product_url)

if product_data:
    # Записываем в JSON файл
    with open('patanjali_products.json', 'w', encoding='utf-8') as f:
        json.dump(product_data, f, indent=4, ensure_ascii=False)
    print("Данные успешно записаны в product.json")
else:
    print("Не удалось получить данные о товаре.")
