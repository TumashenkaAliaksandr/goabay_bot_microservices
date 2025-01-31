import requests
from bs4 import BeautifulSoup

URL = "https://goabay.com/ru/hashtag/turizm-ru/"


def get_tourism_articles():
    """Функция парсит статьи о туризме с сайта goabay.com"""
    response = requests.get(URL)

    if response.status_code != 200:
        return ["Ошибка при получении данных с сайта"]

    soup = BeautifulSoup(response.text, "html.parser")

    articles = []

    for article in soup.find_all("article"):  # Проверь правильную HTML-структуру
        title = article.find("h2")
        description = article.find("p")
        link = article.find("a", href=True)

        if title and link:
            title_text = title.text.strip()
            description_text = description.text.strip() if description else "Нет описания"
            link_url = link["href"]

            articles.append(f"🔹 <b>{title_text}</b>\n{description_text}\n🔗 <a href='{link_url}'>Читать далее</a>")

    return articles[:5]  # Ограничим список до 5 статей
