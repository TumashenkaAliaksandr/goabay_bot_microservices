import requests
from bs4 import BeautifulSoup
import re

def collect_product_links_from_category(category_url):
    """
    Собирает все ссылки на товары с указанной страницы категории.
    """
    try:
        response = requests.get(category_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        product_links = set()

        # Обновленный шаблон регулярного выражения для захвата URL
        # Учитывает возможные дополнительные параметры в URL
        product_link_pattern = re.compile(
            r'https://ishalife\.sadhguru\.org/in/(?![\w-]+/[\w-]+$)(?!bloom$)(?!natural-food$)(?!yogastore$)(?!temple-consecrated$)(?!savetheweave$)(?!marathi$)(?!store-locator$)(?!track-order$)(?!sso-faq$)(?!books-and-dvds$)[\w-]+$'
        )

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if product_link_pattern.match(href):
                product_links.add(href)

        return list(product_links)

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к сайту {category_url}: {e}")
        return []
    except Exception as e:
        print(f"Ошибка при парсинге {category_url}: {e}")
        return []


def collect_all_product_links(category_urls):
    """
    Собирает все ссылки на товары со всех указанных страниц категорий.
    """
    all_product_links = set()
    for url in category_urls:
        product_links = collect_product_links_from_category(url)
        all_product_links.update(product_links)  # Add unique links

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
    ]

    all_product_links = collect_all_product_links(category_urls)

    if all_product_links:
        print("Все ссылки на товары:")
        for link in all_product_links:
            print(link)
        print(f"\nВсего найдено {len(all_product_links)} ссылок.")
    else:
        print("Не удалось получить ссылки на товары.")
