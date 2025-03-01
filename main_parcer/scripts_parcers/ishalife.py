import json
import requests
from bs4 import BeautifulSoup
import re


def parse_isha_product(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        data = {}

        # Название
        title_element = soup.find('span', class_='base')
        data['название'] = title_element.text.strip() if title_element else "Название не найдено"

        # Ссылка на товар
        data['ссылка на товар'] = url

        # Цена
        price_box = soup.find('div', class_='price-box')
        if price_box:
            special_price = price_box.find('span', class_='special-price')
            if special_price:
                price = special_price.find('span', class_='price').text.replace('₹', '').strip()
                data['цена'] = price
            else:
                old_price = price_box.find('span', class_='old-price')
                if old_price:
                    price = old_price.find('span', class_='price').text.replace('₹', '').strip()
                    data['цена'] = price
                else:
                    data['цена'] = "Цена не найдена"
        else:
            data['цена'] = "Цена не найдена"

        # Описание (из product-short-info-wrap)
        short_info_wrap = soup.find('div', class_='product-short-info-wrap')
        if short_info_wrap:
            description_element = short_info_wrap.find('div', class_='product-short-info description')
            if description_element:
                description = description_element.text.strip()
                # Удаляем \r и \n с помощью регулярного выражения и кавычки
                description = re.sub(r'[\r\n\\"]+', ' ', description)
                data['описание'] = description
            else:
                data['описание'] = "Описание не найдено"
        else:
            data['описание'] = "Описание не найдено"

        # Изображения
        image_urls = []
        magic_toolbox = soup.find('div', class_='MagicToolboxContainer')
        if magic_toolbox:
            image_link = magic_toolbox.find('a', class_='MagicZoom')
            if image_link:
                data['фото'] = image_link['href']
            else:
                data['фото'] = "Фото не найдено"
        else:
            data['фото'] = "Фото не найдено"

        # Категория и подкатегории (из breadcrumbs)
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

        # Состав
        # details_element = soup.find('div', class_='product attribute additional-information')
        # data['состав'] = details_element.text.strip() if details_element else "Состав не указан"

        # Размер/Упаковка
        data['размер'] = "100 капсул"

        # By combo
        data['by combo'] = "Да"

        # Информация о доставке
        shipping_info = []
        shipping_wrap = soup.find('div', class_='shipping-wrap')
        if shipping_wrap:
            shipping_blocks = shipping_wrap.find_all('div', class_='shipping-block')
            for block in shipping_blocks:
                text = block.find('p').text.strip()
                shipping_info.append(text)
        data['доставка'] = shipping_info if shipping_info else "Информация о доставке не найдена"

        # SKU (из таблицы "More Information")
        sku = None
        more_info_table = soup.find('table', class_='data table additional-attributes')
        if more_info_table:
            sku_row = more_info_table.find('tr')  # Предполагаем, что SKU в первой строке
            if sku_row:
                sku_label_cell = sku_row.find('td', class_='col label sku')
                sku_data_cell = sku_row.find('td', class_='col data sku')
                if sku_label_cell and sku_data_cell:
                    if sku_label_cell.text.strip() == 'SKU:':  # Убедимся, что это строка с SKU
                        sku = sku_data_cell.text.strip()

        data['SKU'] = sku if sku else "SKU не найден"

        return data

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе {url}: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")
        return None


# Пример использования
product_url = "https://ishalife.sadhguru.org/in/catalog/product/view/id/13458/s/neem-turmeric-powder-in-veg-caps-combo-pack-100nos/"
product_data = parse_isha_product(product_url)

if product_data:
     # Записываем данные в JSON-файл
    with open('jsons/product_ishalife.json', 'w', encoding='utf-8') as f:
        json.dump(product_data, f, indent=4, ensure_ascii=False)
    print("Данные успешно записаны в файл product_data.json")
else:
    print("Не удалось получить данные о товаре.")
