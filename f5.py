from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json  # <~~ ПЕРШИЙ ЕТАП — ІМПОРТУЄМО ІНСТРУМЕНТИ, ЩО ПОТРІБНІ ДЛЯ СКРАПІНГУ
import csv

chrome_options = Options()
chrome_options.add_argument('--headless')        # <--- ДРУГИЙ ЕТАП — НАЛАШТОВУЄМО БРАУЗЕР (РЕЖИМ БЕЗ ВІКНА)
chrome_options.add_argument('--disable-gpu')     # <--- ВИМКНЕННЯ АПАРАТНОГО ПРОСКОРЕННЯ ДЛЯ СУПРОВІДНОГО СЕРВЕРА
chrome_options.add_argument('--no-sanbox')        # <--- ВИМКНЕННЯ ПІСКОВОЇ ОБОЛОНКИ (НА ЛІНУКСІ ІНКОЛИ ПОТРІБНО)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)  # <--- ЗАПУСКАЄМО ХРОМ З ВИЩЕНАЗВАНИМИ НАЛАШТУВАННЯМИ

url = 'https://my.f5.com/manage/s/article/K9412'  # <--- ВСТАВЛЯЄМО ПОТРІБНУ URL-АДРЕСУ
driver.get(url)                                   # <--- ВІДКРИВАЄМО СТОРІНКУ У БРАУЗЕРІ

time.sleep(5)                                     # <--- ЧЕКАЄМО 5 СЕКУНД, ЩОБ ВСЕ ЗАВАНТАЖИЛОСЯ

html = driver.page_source                         # <--- ВИТЯГУЄМО HTML КОД СТОРІНКИ

driver.quit()                                     # <--- ЗАКРИВАЄМО БРАУЗЕР

soup = BeautifulSoup(html, 'html.parser')        # <--- ПЕРЕТВОРЮЄМО HTML В ОБ’ЄКТ ДЛЯ ЛЕГКОГО ПАРСИНГУ

tables = soup.find_all('table')                   # <--- ЗНАХОДИМО ВСІ ТАБЛИЦІ НА СТОРІНЦІ
print(f'Tables found {len(tables)}')              # <--- ВИВОДИМО КІЛЬКІСТЬ ЗНАЙДЕНИХ ТАБЛИЦЬ

# <--- ВИЗНАЧАЄМО СЛОВНИК З НАЗВАМИ КОЛОНОК, ЯКІ НАМ ПОТРІБНО ШУКАТИ, ТА МОЖЛИВІ ВАРІАНТИ ЇХ НАПИСАННЯ
target_headrs = {
    'BIG-IP version': ["big-ip version", "big-ip ver", "version"],
    'Bld': ["bld", "build"],
    "Release date": ["release date", "date"],
    "Supported hardware products": ["supported hardware products", "hardware productc", "supported hardware"]
}

# <--- ФУНКЦІЯ, ЯКА РОЗБИВАЄ ТЕКСТ З АПАРАТНИМ ЗАБЕЗПЕЧЕННЯМ НА СПИСОК ОКРЕМИХ МОДЕЛЕЙ
def split_hardware(text):
    for ch in ['(', ')', '\n']:               # <--- ЗАМІНЮЄМО ДУЖКИ І НОВІ РЯДКИ НА КОМИ
        text = text.replace(ch, ',')
    parts = text.split(',')                   # <--- РОЗДІЛЯЄМО ПО КОМІ
    parts = [p.strip() for p in parts if p.strip()]  # <--- ОЧИЩАЄМО ВІД ПРОБІЛІВ І ПУСТИХ ЕЛЕМЕНТІВ
    return parts

results = []  # <--- СПИСОК ДЛЯ ЗБЕРІГАННЯ ВСІХ ЗНАЙДЕНИХ ЗАПИСІВ

for i, table in enumerate(tables):          # <--- ПРОХОДИМО ПО КОЖНІЙ ТАБЛИЦІ НА СТОРІНЦІ (i — номер таблиці)
    rows = table.find_all('tr')              # <--- ЗНАХОДИМО ВСІ РЯДКИ В ТАБЛИЦІ
    if not rows:                             # <--- ЯКЩО РЯДКІВ НІ, ПРОПУСКАЄМО ТАБЛИЦЮ
        continue

    headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(['th', 'td'])]  # <--- ОТРИМУЄМО ЗАГОЛОВКИ ПЕРШОГО РЯДКА ТАБЛИЦІ І ПРИВОДИМО ЇХ ДО НИЖНЬОГО РЕЄСТРУ
    print(f'Table {i+1} headers {headers}')     # <--- ВИВОДИМО ЗАГОЛОВКИ ДЛЯ ПРОВІРКИ

    headers_map = {}                            # <--- СЛОВНИК ДЛЯ ВІДПОВІДНОСТІ НАЗВ КОЛОНОК І ЇХ ІНДЕКСІВ
    for idx, h in enumerate(headers):          # <--- ПРОХОДИМО ПО КОЖНОМУ ЗАГОЛОВКУ З ТАБЛИЦІ
        for key, variants in target_headrs.items():   # <--- ПЕРЕВІРЯЄМО, ЧИ Є В ТЕКСТІ ЗАГОЛОВКА ОДИН ІЗ ВАРІАНТІВ З НАШОГО СЛОВНИКА
            if any(v in h for v in variants):    # <--- ЯКЩО Є СХОЖИЙ ВАРІАНТ, ЗАПИСУЄМО ІНДЕКС КОЛОНКИ ПІД ВІДПОВІДНИМ КЛЮЧЕМ
                headers_map[key] = idx
                break

    if not headers_map:  # <--- ЯКЩО НЕ ЗНАЙШЛОСЯ ПОТРІБНИХ КОЛОНОК — ПРОПУСКАЄМО ТАБЛИЦЮ
        print(f'Table {i+1} пропущена - немає потрібних заголовків')
        continue

    for row in rows[1:]:         # <--- ПРОХОДИМО ПО ВСІХ РЯДКАХ ТАБЛИЦІ, КРІМ ЗАГОЛОВКА
        cells = row.find_all(['td', 'th'])   # <--- ОТРИМУЄМО В КОЖНОМУ РЯДКУ ВСІ ЯЧЕЙКИ
        if not cells:                       # <--- ЯКЩО ЯЧЕЙОК НІ, ПРОПУСКАЄМО РЯДОК
            continue

        entry = {}                       # <--- СЛОВНИК ДЛЯ ЗБЕРІГАННЯ ДАНИХ З РЯДКА

        for key, idx in headers_map.items():    # <--- ЗБИРАЄМО ПОТРІБНІ ДАНІ З ЯЧЕЙОК ЗА ІНДЕКСАМИ
            text = cells[idx].get_text(strip=True) if idx < len(cells) else ""
            entry[key] = text

        big_ip_text = entry.get("BIG-IP version", "")                     # <--- ОКРЕМІ ЗНАЧЕННЯ ЗАПИСУЄМО В ПЕРЕМІННІ
        existing_hw = entry.get("Supported hardware products", "")
        combined = ','.join(filter(None, [existing_hw, big_ip_text]))       # <--- ОБ’ЄДНУЄМО ЇХ В ОДИН РЯДОК (ЯКЩО Є ОБИДВА)
        entry["Supported hardware products"] = split_hardware(combined)   # <--- РОЗБИВАЄМО ЦЕЙ РЯДОК НА СПИСОК МОДЕЛЕЙ
        entry["BIG-IP version"] = big_ip_text.strip()                      # <--- ЗАЛИШАЄМО BIG-IP VERSION ЯК Є

        results.append(entry)          # <--- ДОДАЄМО ЗАПИС У СПИСОК РЕЗУЛЬТАТІВ

print(f"Знайдено записів: {len(results)}")   # <--- ВИВОДИМО КІЛЬКІСТЬ ЗАПИСІВ

# <--- ЗБЕРІГАЄМО РЕЗУЛЬТАТИ У ФАЙЛ JSON З ВІДСТУПАМИ І КОДУВАННЯМ UTF-8
with open("f5_data.json", "w", encoding="utf-8") as f_json:
    json.dump(results, f_json, indent=4, ensure_ascii=False)

csv_headers = ["BIG-IP version", "Bld", "Release date", "Supported hardware products", "EUD", "AOM"]

# <--- ЗБЕРІГАЄМО РЕЗУЛЬТАТИ У CSV, КОНВЕРТУЮЧИ СПИСКИ В РЯДКИ ЧЕРЕЗ ";"
with open("f5_data.csv", "w", newline='', encoding="utf-8") as f_csv:
    writer = csv.DictWriter(f_csv, fieldnames=csv_headers)
    writer.writeheader()
    for entry in results:
        row = {}
        for h in csv_headers:
            val = entry.get(h, "")
            if isinstance(val, list):
                val = "; ".join(val)
            row[h] = val
        writer.writerow(row)