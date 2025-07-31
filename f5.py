from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
import csv

# === 1. Налаштування опцій для запуску браузера в headless-режимі ===
chrome_options = Options()
chrome_options.add_argument('--headless')         # Без відкриття вікна браузера
chrome_options.add_argument('--disable-gpu')      # Вимкнення апаратного прискорення
chrome_options.add_argument('--no-sandbox')       # Для Linux-систем

# === 2. Ініціалізація драйвера Chrome ===
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# === 3. Відкриваємо сторінку F5 ===
url = 'https://my.f5.com/manage/s/article/K9412'
driver.get(url)
time.sleep(5)  # Чекаємо завантаження контенту

# === 4. Отримуємо HTML та закриваємо браузер ===
html = driver.page_source
driver.quit()

# === 5. Парсимо HTML за допомогою BeautifulSoup ===
soup = BeautifulSoup(html, 'html.parser')
tables = soup.find_all('table')
print(f'Знайдено таблиць: {len(tables)}')

# === 6. Ключі для пошуку заголовків у таблицях ===
target_headers = {
    'BIG-IP version': ["big-ip version", "big-ip ver", "version"],
    'Bld': ["bld", "build"],
    "Release date": ["release date", "date"],
    "Supported hardware products": ["supported hardware products", "hardware products", "supported hardware"],
    'EUD': ["eud"],
    'AOM': ["aom"]
}

# === 7. Функція для розділення назв апаратного забезпечення ===
def split_hardware(text):
    for ch in ['(', ')', '\n']:
        text = text.replace(ch, ',')
    parts = text.split(',')
    parts = [p.strip() for p in parts if p.strip()]
    return parts

# === 8. Список для збереження результатів ===
results = []

# === 9. Проходимо по кожній таблиці ===
for i, table in enumerate(tables):
    rows = table.find_all('tr')
    if not rows:
        continue

    # Отримуємо заголовки
    headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(['th', 'td'])]
    print(f'Таблиця {i+1} заголовки: {headers}')

    # Створюємо мапу заголовків
    headers_map = {}
    for idx, h in enumerate(headers):
        for key, variants in target_headers.items():
            if any(v in h for v in variants):
                headers_map[key] = idx
                break

    if not headers_map:
        print(f'Таблиця {i+1} пропущена - немає потрібних заголовків')
        continue

    # Обробка рядків таблиці
    for row in rows[1:]:
        cells = row.find_all(['td', 'th'])
        if not cells:
            continue

        entry = {}
        for key, idx in headers_map.items():
            text = cells[idx].get_text(strip=True) if idx < len(cells) else ""
            entry[key] = text

        # Обробка поля hardware
        big_ip_text = entry.get("BIG-IP version", "")
        existing_hw = entry.get("Supported hardware products", "")
        combined = ', '.join(filter(None, [existing_hw, big_ip_text]))
        entry["Supported hardware products"] = split_hardware(combined)
        entry["BIG-IP version"] = big_ip_text.strip()

        results.append(entry)

print(f"Знайдено записів: {len(results)}")

# === 10. Збереження у JSON ===
with open("Scrape.json", 'w', encoding='utf-8') as file:
    json.dump(results, file, ensure_ascii=False, indent=4)

# === 11. Збереження у CSV ===
csv_headers = ['BIG-IP version', 'Bld', "Release date", "Supported hardware products", 'EUD', "AOM"]

with open('scrape.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

    for entry in results:
        row = {}
        for h in csv_headers:
            val = entry.get(h, "")
            if isinstance(val, list):
                val = "; ".join(val)


Ось **повністю коментований код у твоєму стилі пояснень по етапах** – як ти робив раніше. Коментарі збережено простими, зрозумілими і покроковими 👇

---

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json                # <~~~ ПЕРШИЙ ЕТАП — ІМПОРТ ВСІХ ІНСТРУМЕНТІВ
import csv

# === ДРУГИЙ ЕТАП — НАСТРОЮЄМО ОПЦІЇ ДЛЯ БРАУЗЕРА, ЩОБ ВІН ПРАЦЮВАВ В ТІНІ (без GUI)
chrome_options = Options()
chrome_options.add_argument('--headless')        # запускаємо в headless (без вікна браузера)
chrome_options.add_argument('--disable-gpu')     # вимикаємо GPU (не обов’язково, але бажано)
chrome_options.add_argument('--no-sandbox')      # потрібно для Linux (наприклад, у Docker)

# === ТРЕТІЙ ЕТАП — ЗАПУСКАЄМО ДРАЙВЕР CHROME
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# === ЧЕТВЕРТИЙ ЕТАП — ПЕРЕХІД ЗА ПОСИЛАННЯМ
url = 'https://my.f5.com/manage/s/article/K9412'  # наше посилання
driver.get(url)                                   # відкриваємо сторінку
time.sleep(5)                                     # даємо час на повне завантаження

# === ПʼЯТИЙ ЕТАП — ОТРИМУЄМО HTML-КОД І ЗАКРИВАЄМО БРАУЗЕР
html = driver.page_source                         # зберігаємо HTML-код сторінки
driver.quit()                                     # закриваємо браузер

# === ШОСТИЙ ЕТАП — ПІДКЛЮЧАЄМО BEAUTIFULSOUP І ШУКАЄМО ВСІ ТАБЛИЦІ
soup = BeautifulSoup(html, 'html.parser')
tables = soup.find_all('table')
print(f'Знайдено таблиць: {len(tables)}')

# === СЬОМИЙ ЕТАП — СЛОВНИК З МОЖЛИВИМИ НАЗВАМИ КОЛОНОК
target_headers = {
    'BIG-IP version': ["big-ip version", "big-ip ver", "version"],
    'Bld': ["bld", "build"],
    "Release date": ["release date", "date"],
    "Supported hardware products": ["supported hardware products", "hardware products", "supported hardware"],
    'EUD': ["eud"],
    'AOM': ["aom"]
}

# === ВОСЬМИЙ ЕТАП — ФУНКЦІЯ ДЛЯ РОЗБИВКИ ТЕКСТУ НА ЧАСТИНИ
def split_hardware(text):
    for ch in ['(', ')', '\n']:               # міняємо дужки і перенос рядка на кому
        text = text.replace(ch, ',')
    parts = text.split(',')                   # розбиваємо по комах
    parts = [p.strip() for p in parts if p.strip()]  # очищаємо і прибираємо пусті
    return parts

# === ДЕВʼЯТИЙ ЕТАП — СПИСОК, КУДИ МИ БУДЕМО ЗБИРАТИ ВСІ ДАНІ
results = []

# === ДЕСЯТИЙ ЕТАП — ПРОХОДИМОСЬ ПО ВСІХ ТАБЛИЦЯХ
for i, table in enumerate(tables):
    rows = table.find_all('tr')                      # знаходимо рядки в таблиці
    if not rows:                                     # якщо таблиця порожня — ігноруємо
        continue

    # === ОДИНАДЦЯТИЙ ЕТАП — ЗНАХОДИМО ЗАГОЛОВКИ І ЗМІНЮЄМО НА МАЛІ БУКВИ
    headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(['th', 'td'])]
    print(f'Таблиця {i+1} заголовки: {headers}')

    headers_map = {}  # словник для мапи заголовків

    # === ДВАНАДЦЯТИЙ ЕТАП — ЗНАХОДИМО ПОТРІБНІ ЗАГОЛОВКИ
    for idx, h in enumerate(headers):
        for key, variants in target_headers.items():
            if any(v in h for v in variants):        # якщо хоча б один варіант підходить
                headers_map[key] = idx               # запам’ятовуємо індекс колонки
                break

    if not headers_map:                              # якщо немає жодного корисного заголовка
        print(f'Таблиця {i+1} пропущена — немає потрібних колонок')
        continue

    # === ТРИНАДЦЯТИЙ ЕТАП — ПРОХОДИМО ПО ВСІХ РЯДКАХ ТАБЛИЦІ
    for row in rows[1:]:
        cells = row.find_all(['td', 'th'])           # шукаємо комірки
        if not cells:
            continue

        entry = {}

        # === ЧОТИРНАДЦЯТИЙ ЕТАП — ВИТЯГУЄМО ТЕКСТ ІЗ КОЖНОЇ КОЛОНКИ
        for key, idx in headers_map.items():
            text = cells[idx].get_text(strip=True) if idx < len(cells) else ""
            entry[key] = text

        # === П'ЯТНАДЦЯТИЙ ЕТАП — ОБРОБЛЯЄМО HARDWARE + ВЕРСІЮ
        big_ip_text = entry.get("BIG-IP version", "")
        existing_hw = entry.get("Supported hardware products", "")
        combined = ', '.join(filter(None, [existing_hw, big_ip_text]))
        entry["Supported hardware products"] = split_hardware(combined)
        entry["BIG-IP version"] = big_ip_text.strip()

        results.append(entry)  # додаємо запис до загального списку

# === ШІСТНАДЦЯТИЙ ЕТАП — ВИВОДИМО СКІЛЬКИ ЗАПИСІВ ЗНАЙШЛИ
print(f"Знайдено записів: {len(results)}")

# === СІМНАДЦЯТИЙ ЕТАП — ЗАПИСУЄМО В JSON
with open("Scrape.json", 'w', encoding='utf-8') as file:
    json.dump(results, file, ensure_ascii=False, indent=4)

# === ВІСІМНАДЦЯТИЙ ЕТАП — ЗАПИСУЄМО В CSV
csv_headers = ['BIG-IP version', 'Bld', "Release date", "Supported hardware products", 'EUD', "AOM"]
with open('scrape.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()
    for entry in results:
        row = {}
        for h in csv_headers:
            val = entry.get(h, "")
            if isinstance(val, list):      # якщо список — перетворюємо у строку
                val = "; ".join(val)
            row[h] = val
        writer.writerow(row)