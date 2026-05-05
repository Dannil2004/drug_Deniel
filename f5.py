
# Import required libraries
import requests                    # Used for sending HTTP requests
from bs4 import BeautifulSoup     # Used for parsing HTML content
import json                       # Used for saving data in JSON format
import csv                        # Used for saving data in CSV format
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# --- STEP 1: Configure Chrome options (headless mode for automation) ---
chrome_options = Options()
chrome_options.add_argument('--headless')        # Run browser in background (no UI)
chrome_options.add_argument('--disable-gpu')     # Disable GPU acceleration (for stability)
chrome_options.add_argument('--no-sandbox')      # Disable sandbox (often needed on Linux servers)


# --- STEP 2: Initialize WebDriver ---
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)


# --- STEP 3: Open target URL ---
url = 'https://my.f5.com/manage/s/article/K9412'
driver.get(url)


# --- STEP 4: Wait for page to load (basic approach) ---
time.sleep(5)   # In real projects лучше использовать WebDriverWait


# --- STEP 5: Extract HTML content ---
html = driver.page_source


# --- STEP 6: Close browser ---
driver.quit()


# --- STEP 7: Parse HTML with BeautifulSoup ---
soup = BeautifulSoup(html, 'html.parser')


# --- STEP 8: Find all tables on the page ---
tables = soup.find_all('table')
print(f'Tables found: {len(tables)}')


# --- STEP 9: Define target headers and their possible variations ---
target_headers = {
    'BIG-IP version': ["big-ip version", "big-ip ver", "version"],
    'Bld': ["bld", "build"],
    "Release date": ["release date", "date"],
    "Supported hardware products": [
        "supported hardware products",
        "hardware productc",
        "supported hardware"
    ]
}


# --- Helper function: Split hardware text into a clean list ---
def split_hardware(text):
    # Replace unwanted characters with commas
    for ch in ['(', ')', '\n']:
        text = text.replace(ch, ',')

    # Split string into parts
    parts = text.split(',')

    # Clean whitespace and remove empty values
    parts = [p.strip() for p in parts if p.strip()]

    return parts


# --- STEP 10: Extract data from tables ---
results = []

for i, table in enumerate(tables):

    rows = table.find_all('tr')

    if not rows:
        continue  # Skip empty tables


    # Extract headers from the first row
    headers = [
        th.get_text(strip=True).lower()
        for th in rows[0].find_all(['th', 'td'])
    ]

    print(f'Table {i+1} headers: {headers}')


    # Map detected headers to target fields
    headers_map = {}

    for idx, h in enumerate(headers):
        for key, variants in target_headers.items():
            if any(v in h for v in variants):
                headers_map[key] = idx
                break


    # Skip table if required headers are not found
    if not headers_map:
        print(f'Table {i+1} skipped - required headers not found')
        continue


    # --- Extract data rows ---
    for row in rows[1:]:

        cells = row.find_all(['td', 'th'])

        if not cells:
            continue


        entry = {}

        # Extract values based on mapped column indexes
        for key, idx in headers_map.items():
            text = cells[idx].get_text(strip=True) if idx < len(cells) else ""
            entry[key] = text


        # --- Data cleaning and normalization ---
        big_ip_text = entry.get("BIG-IP version", "")
        existing_hw = entry.get("Supported hardware products", "")

        # Combine hardware + version for better parsing
        combined = ','.join(filter(None, [existing_hw, big_ip_text]))

        # Convert to list
        entry["Supported hardware products"] = split_hardware(combined)

        # Clean version text
        entry["BIG-IP version"] = big_ip_text.strip()


        results.append(entry)


print(f"Total records found: {len(results)}")


# --- STEP 11: Save results to JSON ---
with open("f5_data.json", "w", encoding="utf-8") as f_json:
    json.dump(results, f_json, indent=4, ensure_ascii=False)


# --- STEP 12: Save results to CSV ---
csv_headers = [
    "BIG-IP version",
    "Bld",
    "Release date",
    "Supported hardware products",
    "EUD",
    "AOM"
]

with open("f5_data.csv", "w", newline='', encoding="utf-8") as f_csv:

    writer = csv.DictWriter(f_csv, fieldnames=csv_headers)
    writer.writeheader()

    for entry in results:
        row = {}

        for h in csv_headers:
            val = entry.get(h, "")

            # Convert lists to string for CSV format
            if isinstance(val, list):
                val = "; ".join(val)

            row[h] = val

        writer.writerow(row)
