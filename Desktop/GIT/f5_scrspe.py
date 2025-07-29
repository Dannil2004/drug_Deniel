from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
import csv

# Налаштування Chrome у безголовому режимі (без відкриття вікна браузера)
chrome_options = Options()
chrome_options.add_argument("--headless")       # Режим без GUI
chrome_options.add_argument("--disable-gpu")    # Вимкнути апаратне прискорення
chrome_options.add_argument("--no-sandbox")     # Вимкнути sandbox (для Linux-систем)

# Автоматично завантажуємо та встановлюємо потрібний драйвер Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Вказуємо URL сторінки для парсингу
url = "https://my.f5.com/manage/s/article/K9412"
driver.get(url)

# Чекаємо 5 секунд, щоб сторінка повністю завантажилася
time.sleep(5)

# Отримуємо HTML-код сторінки
html = driver.page_source

# Закриваємо браузер
driver.quit()

# Парсимо HTML за допомогою BeautifulSoup
soup = BeautifulSoup(html, "html.parser")

# Знаходимо всі таблиці на сторінці
tables = soup.find_all("table")
print(f"Знайдено таблиць: {len(tables)}")

# Ключі для пошуку потрібних заголовків таблиці і варіанти написання
target_headers = {
    "BIG-IP version": ["big-ip version", "big-ip ver", "version"],
    "Bld": ["bld", "build"],
    "Release date": ["release date", "date"],
    "Supported hardware products": ["supported hardware products", "hardware products", "supported hardware"],
    "EUD": ["eud"],
    "AOM": ["aom"]
}

# Функція для розділення рядка з апаратним забезпеченням на список окремих моделей
def split_hardware(text):
    # Замінюємо дужки та символи нового рядка на коми
    for ch in ['(', ')', '\n']:
        text = text.replace(ch, ',')
    # Розділяємо рядок по комах і очищуємо від зайвих пробілів
    parts = text.split(',')
    parts = [p.strip() for p in parts if p.strip()]  # Видаляємо пусті елементи
    return parts

results = []

# Обробляємо кожну таблицю на сторінці
for i, table in enumerate(tables):
    rows = table.find_all("tr")
    if not rows:
        continue

    # Збираємо заголовки таблиці, приводимо до нижнього регістру для пошуку
    headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(["th", "td"])]
    print(f"Таблиця {i+1} заголовки: {headers}")

    header_map = {}
    # Визначаємо індекси потрібних стовпців за ключами
    for idx, h in enumerate(headers):
        for key, variants in target_headers.items():
            if any(v in h for v in variants):
                header_map[key] = idx
                break

    # Якщо немає потрібних заголовків — пропускаємо таблицю
    if not header_map:
        print(f"Таблиця {i+1} пропущена - немає потрібних заголовків")
        continue

    # Парсимо всі рядки таблиці, окрім заголовку
    for row in rows[1:]:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue

        entry = {}
        # Збираємо дані з потрібних колонок за індексами
        for key, idx in header_map.items():
            text = cells[idx].get_text(strip=True) if idx < len(cells) else ""
            entry[key] = text

        # Об’єднуємо значення BIG-IP version і Supported hardware products в один список для зручності
        big_ip_text = entry.get("BIG-IP version", "")
        existing_hw = entry.get("Supported hardware products", "")
        combined = ", ".join(filter(None, [existing_hw, big_ip_text]))
        # Розбиваємо комбінований рядок на список моделей
        entry["Supported hardware products"] = split_hardware(combined)
        # Залишаємо BIG-IP version як є
        entry["BIG-IP version"] = big_ip_text.strip()

        results.append(entry)

print(f"Знайдено записів: {len(results)}")

# Зберігаємо результати у JSON файл з відступами та кодуванням UTF-8
with open("f5_data.json", "w", encoding="utf-8") as f_json:
    json.dump(results, f_json, indent=4, ensure_ascii=False)

# Зберігаємо результати у CSV файл
csv_headers = ["BIG-IP version", "Bld", "Release date", "Supported hardware products", "EUD", "AOM"]
with open("f5_data.csv", "w", newline='', encoding="utf-8") as f_csv:
    writer = csv.DictWriter(f_csv, fieldnames=csv_headers)
    writer.writeheader()
    for entry in results:
        row = {}
        for h in csv_headers:
            val = entry.get(h, "")
            # Якщо поле список, з'єднуємо елементи рядком через "; "
            if isinstance(val, list):
                val = "; ".join(val)
            row[h] = val
        writer.writerow(row)
