import requests
from bs4 import BeautifulSoup
import json

class ScraperHelper:
    def fetch_html(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
   
    def parse_html(self, html):
        return BeautifulSoup(html, 'html.parser')

    def save_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class AbodeScraper:
    def __init__(self):
        self.base_url = 'https://helpx.adobe.com/support/programs/eol-matrix.html'
        self.data = []

    def scrape(self):
        helper = ScraperHelper()
        html = helper.fetch_html(self.base_url)
        soup = helper.parse_html(html)

        table = soup.find("table")
        if not table:
            print("Таблиця не знайдена")
            return

        rows = table.find_all("tr")[1:]  # пропускаємо заголовок
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 6:
                product_name = cols[0].text.strip()
                version = cols[1].text.strip()
                build = cols[2].text.strip()
                general_availability = cols[3].text.strip()
                end_of_core_support = cols[4].text.strip()
                end_of_extended_support = cols[5].text.strip()

                self.data.append({
                    'product_name': product_name,
                    'version': version,
                    'build': build,
                    'general_availability': general_availability,
                    'end_of_core_support': end_of_core_support,
                    'end_of_extended_support': end_of_extended_support
                })

        helper.save_to_json(self.data, 'all_products.json')
        print(f"Збережено {len(self.data)} записів у all_products.json")


def main():
    scraper = AbodeScraper()
    scraper.scrape()


if __name__ == '__main__':
    main()
