import requests
import json
from bs4 import BeautifulSoup

def scrape_bestsellers(url):
    """
    Парсит блок "Yogic Best Sellers" с сайта ishalife.sadhguru.org.

    Args:
        url (str): URL главной страницы сайта.

    Returns:
        list: Список словарей, содержащих информацию о каждом товаре-бестселлере.
              Возвращает пустой список в случае ошибки.
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
            image_src = item.find('img', class_='product-image-photo')['src']
            price = item.find('span', class_='price').text.strip()
            try:
                rating_element = item.find('div', class_='rating-result')
                rating_title = rating_element['title']
                rating = rating_title
            except:
                rating = "Рейтинг отсутствует"
            products.append({
                'name': name,
                'link': link,
                'image_src': image_src,
                'price': price,
                'rating': rating
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
            print(f"  Изображение: {product['image_src']}")
            print(f"  Цена: {product['price']}")
            print(f"  Рейтинг: {product['rating']}")
            print("-" * 30)

        # Сохраняем данные в JSON-файл
        with open('jsons/isha_bestsellers_products.json', 'w', encoding='utf-8') as f:
            json.dump(bestsellers, f, ensure_ascii=False, indent=4)
    else:
        print("Не удалось получить бестселлеры.")
