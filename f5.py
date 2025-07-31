from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json.                               #<~~ ПЕРШИЙ ЄТАП ІМПОРТ ІНСТРУМЕНТІВ 
import csv

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu').    #<~~~ ДРУГИЙ ПОТІМ МИ НАСТРЮЄМ БРАУЗЄР
chrome_options.add_argument('--no-sanbox')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service,options=chrome_options).       #<~~~ ТРЕТІЙПОТІМ ТРЕБА ЦЕ ЗАПУСТИТИ 

url = 'https://my.f5.com/manage/s/article/K9412'.        #<~~~ ЧЕТРЕРТИЙ ЄТАП ЦЕ ЗАПИТ ЮРЛ ЗАПУСК
#ЧЕКАННЯ ЗАКОУЗКИ ПОЛУЧЕНІЄ ХТМЛ І ЗАКРИТТЯЯ
driver.get(url)

time.sleep(5)

html = driver.page_source

driver.quit()

soup = BeautifulSoup(html,'html.parser').  #<~~ ПЯТИЙ ЄТАП ЦЕ ПІДКЛЮЧЕННЯ СУПА І ПОШУК ВИХ ТАБЛИЦ

tables = soup.find_all('table')
print(f'Tables found{len(tables)}')

target_headrs = {
    'BIG-IP version' : ["big-ip version",
    "big-ip ver","version"],
    'Bld' : ["bld","build"],
    "Release date" : ["release date","date"],       #<~~~. ШОСТИЙ ЄТАП ЦЕ СТВОРЕННЯ СЛОВНИКА З ВОЗМОЖНИМИ НАЗВАМИ ТОГО ШО НАМ НАДЛ НАЙТИ 
    "Supported hardware products" : ["supported hardware products","hardware productc","supported hardware"]}


def split_hardware(text):
    for ch in ['(',')','\n']:
        text = text.replace(ch,',').   #<~~~~ Сьмий Тут ми змінюємо всі знаки на коми
    parts = text.split(',')
    parts = [p.strip() for p in parts if p.strip()]
    return parts

results = [].   #<~~~ СЬОМИМ ЄТАПОМ Є СТВОРЕННЯ ЛІСТИ ДОЯ ПЕРЕХОВУВАННЯ ГОТОВИХ ДАННИХ З ТАБЛИЦІ 

for i,table in enumerate(tables):
    rows = table.find_all('tr').   #<~~ ВОСЬМИМ ЄТАПОМ Є ВИВЕДЕННЯ КІЛЬКОСТІ ТАБЛТЦЬ І ПЕРЕВОДА ЇХ В МАЛЕНЬКІ ЛІТЕРИ 
    if not rows:
        continue

    headers = [th.get_text(strip = True).lower() for th in rows[0].find_all(['th','td'])]
    print(f'Table {i+1} headers{headers}')

    headers_map = {}

    for idx,h in enumerate(headers):
            for key, variants in target_headrs.items():
                if any (v in h for v in variants):
                    headers_map[key] = idx
                break

            if not headers_map:
                print(f'Tble{i+1} is missing no required headers')
            continue

    for row in rows[1:]:
        cells = row.find_all(['td','th'])
        if not cells:
            continue
             
        entry = {}


        for key, idx in headers_map.items():
            text = cells[idx].get_text(strip = True) if idx <len(cells) else "" 
            entry[key] = text

        big_ip_text = entry.get("BIG-IP version", "")
        existing_hw = entry.get("Supported hardware productc", "")
        combineid = ','.join(filter(None,[existing_hw,big_ip_text]))
        entry["Supported hardware productc"] = split_hardware(combineid)
        entry["BIG-IP version"] = big_ip_text.strip()
        results.append(entry)
print(f"Found records{len(results)}")

with open("Scrape.json", 'w', encoding='utf-8') as file:
                  json.dump(results,file,ensure_ascii=False,indent=4)

csv_headers = ['BIG_IP version', 'bld',"Release date", "Supported hardware productc", 'EUD',"AOM"]
with open('scrape.csv','w',newline='',encoding='utf-8') as file:
     wrinter = csv.DictWriter(file,fieldnames=csv_headers)
     wrinter.writeheader()
     for entry in results:
        row = {}
        for h in csv_headers:
            val = entry.get(h,"")
            if isinstance(val,list):
                val = ";".join(val)
            row[h] = val
        wrinter.writerow(row)
                 


    
    








