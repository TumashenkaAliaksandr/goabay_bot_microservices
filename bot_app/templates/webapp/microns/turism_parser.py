from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ---- ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ СТАТЕЙ ----
def get_tourism_articles_selenium():
    """
    Получает 5 последних статей о туризме с сайта goabay.com.
    Использует Selenium с эмуляцией браузера и защитой от блокировки.
    """
    URL = "https://goabay.com/ru/hashtag/turizm-ru/"

    # ---- НАСТРОЙКИ ДЛЯ ОБХОДА БЛОКИРОВОК ----
    options = Options()
    options.add_argument("--headless")  # Без GUI (ускоряет работу)
    options.add_argument("--incognito")  # Инкогнито-режим (чистый кеш)
    options.add_argument("--window-size=1920,1080")  # Фиксированный размер окна

    # --- Добавляем User-Agent ---
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/134.0"
    options.set_preference("general.useragent.override", user_agent)

    # --- Оптимизация Firefox (ускорение загрузки) ---
    options.set_preference("browser.startup.homepage_override.mstone", "ignore")
    options.set_preference("startup.homepage_welcome_url.additional", "about:blank")
    options.set_preference("browser.tabs.remote.autostart", False)
    options.set_preference("browser.privatebrowsing.autostart", True)
    options.set_preference("network.http.pipelining", True)
    options.set_preference("network.http.proxy.pipelining", True)
    options.set_preference("network.dns.disableIPv6", True)
    options.set_preference("media.peerconnection.enabled", False)

    # --- (Опционально) Отключаем загрузку картинок и CSS ---
    options.set_preference("permissions.default.image", 2)
    options.set_preference("browser.display.use_document_fonts", 0)
    options.set_preference("browser.cache.memory.enable", False)
    options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", False)

    # --- Указываем путь к драйверу вручную (ускорение) ---
    GECKODRIVER_PATH =  r"C:\Users\Phoenix_Pegasus\.wdm\drivers\geckodriver\win64\v0.35.0\geckodriver.exe" #  для сервера путь гикодрайвера "/usr/local/bin/geckodriver"
    service = Service(GECKODRIVER_PATH)
    driver = webdriver.Firefox(service=service, options=options)

    try:
        print("🔄 Открываем сайт:", URL)
        driver.get(URL)

        # --- ПРОВЕРЯЕМ, НЕ ОШИБКА ЛИ 403 ---
        if "403 Forbidden" in driver.page_source:
            print("🚨 Сайт недоступен! Попробуйте включить VPN или использовать прокси.")
            return [{"error": "Сайт недоступен. Включите VPN."}]

        # --- ПРОКРУЧИВАЕМ СТРАНИЦУ ВНИЗ ДЛЯ ПОДГРУЗКИ СТАТЕЙ ---
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # --- НАХОДИМ СПИСОК СТАТЕЙ ---
        wait = WebDriverWait(driver, 0.1)
        articles_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "posts-list")))
        articles = articles_container.find_elements(By.TAG_NAME, "article")

        print(f"✅ Найдено статей: {len(articles)}")

        articles_data = []
        for i, article in enumerate(articles[:5]):  # Берем первые 5 статей
            try:
                title_element = article.find_element(By.CSS_SELECTOR, "h4.entry-title a")
                title_text = title_element.text.strip() if title_element.text else "Без названия"
                link_url = title_element.get_attribute("href").strip() if title_element.get_attribute("href") else "Нет ссылки"

                # Попробуем получить дату
                try:
                    date_element = article.find_element(By.TAG_NAME, "time")
                    date_text = date_element.text.strip() if date_element.text else "Без даты"
                except:
                    date_text = "Без даты"

                # Выводим статью в консоль
                print(f"📌 Статья {i + 1}: {title_text} ({date_text})")
                print(f"🔗 Ссылка: {link_url}")

                # Подготавливаем данные для Telegram
                articles_data.append({
                    "title": title_text,
                    "date": date_text,
                    "link": link_url
                })
            except Exception as e:
                print(f"⚠️ Ошибка при обработке статьи {i + 1}: {e}")

        return articles_data


    except Exception as e:
        print(f"❌ Ошибка при загрузке страницы: {e}")
        return [{"error": f"Ошибка при загрузке страницы: {e}"}]

    finally:
        driver.quit()

