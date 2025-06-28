from bs4 import BeautifulSoup

def extract_price(soup):
    """
    Универсальный парсер цены для разных версий вёрстки.
    Возвращает кортеж (sale_price, original_price), где значения — строки или None.
    """

    # 1. Попытка найти цену со скидкой (sale price)
    sale_price = None
    original_price = None

    # Список возможных data-test-id для цены со скидкой
    sale_price_ids = [
        'item-sale-price-pdp',
        'item-price-pdp',  # Иногда обычная цена без скидки
    ]
    # Список возможных data-test-id для оригинальной цены
    original_price_ids = [
        'item-original-price-pdp',
        'item-strike-price-pdp',
    ]

    # 1.1. Поиск по data-test-id (sale)
    for test_id in sale_price_ids:
        tag = soup.find('span', {'data-test-id': test_id})
        if tag and tag.get_text(strip=True):
            sale_price = tag.get_text(strip=True)
            break

    # 1.2. Поиск по data-test-id (original)
    for test_id in original_price_ids:
        tag = soup.find('span', {'data-test-id': test_id})
        if tag and tag.get_text(strip=True):
            original_price = tag.get_text(strip=True)
            break

    # 2. Если не найдено, ищем по классам (например, font-bold для sale)
    if not sale_price:
        tag = soup.find('span', class_=['font-bold', 'text-base', 'override:md:text-2xl'])
        if tag and tag.get_text(strip=True):
            sale_price = tag.get_text(strip=True)

    # 3. Если не найдено, ищем в price region по символу валюты
    if not sale_price:
        price_region = soup.find('div', {'data-test-id': 'pdp-price-region'})
        if price_region:
            tag = price_region.find('span', string=lambda s: s and any(x in s for x in ['₹', '$', '₽', '€']))
            if tag and tag.get_text(strip=True):
                sale_price = tag.get_text(strip=True)

    # 4. Если всё равно не найдено, ищем любой span с символом валюты
    if not sale_price:
        tag = soup.find('span', string=lambda s: s and any(x in s for x in ['₹', '$', '₽', '€']))
        if tag and tag.get_text(strip=True):
            sale_price = tag.get_text(strip=True)

    # 5. Если не найдено оригинальной цены, ищем зачёркнутую цену (strike, line-through)
    if not original_price:
        tag = soup.find('span', style=lambda s: s and 'line-through' in s)
        if tag and tag.get_text(strip=True):
            original_price = tag.get_text(strip=True)

    # 6. Если не найдено, ищем по классам, связанным с зачёркнутой ценой
    if not original_price:
        tag = soup.find('span', class_=['line-through', 'strike', 'old-price'])
        if tag and tag.get_text(strip=True):
            original_price = tag.get_text(strip=True)

    return sale_price, original_price

# Пример использования:
# soup = BeautifulSoup(html, 'html.parser')
# sale_price, original_price = extract_price(soup)
# print('Sale price:', sale_price)
# print('Original price:', original_price)
