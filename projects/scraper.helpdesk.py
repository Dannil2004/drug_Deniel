import requests
from bs4 import BeautifulSoup, Comment
import json

class HelperScraper:
    def fetch_html(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        raise Exception(f"Не вдалося завантажити {url}")

    def parse_html(self, html):
        return BeautifulSoup(html, 'html.parser')

    def save_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


class HelpdeskAndMacroScraper:
    def __init__(self, urls):
        self.urls = urls
        self.helper = HelperScraper()
        self.result = {}

    def run(self):
        for name, url in self.urls.items():
            print(f"Обробляю {name}: {url}")
            html = self.helper.fetch_html(url)
            soup = self.helper.parse_html(html)

            if name == "macro":
                self.result[name] = self.scrape_macro(soup)
            elif name == "helpdesk":
                self.result[name] = self.scrape_helpdesk(soup)

        self.helper.save_to_json(self.result, "versions.json")
        print("Дані збережено у versions.json")

    def scrape_macro(self, soup):
        releases = []
        for div in soup.find_all('div', class_='mt3'):
            comments = []
            for element in div.children:
                if isinstance(element, Comment):
                    comments.append(element)

            if comments:
                version = comments[0].strip()
            else:
                version = "Unknown version"

            details_list = [t for t in div.stripped_strings if not isinstance(t, Comment)]
            details = ' '.join(details_list).strip()

            releases.append({'version': version, 'details': details})

        return releases

    def scrape_helpdesk(self, soup):
        releases = []
        for h2 in soup.find_all('h2'):
            version = h2.get_text(strip=True)
            sibling = h2
            details = []
            while sibling := sibling.find_next_sibling():
                if sibling.name == 'ul':
                    details = [li.get_text(strip=True) for li in sibling.find_all('li')]
                    break
            if details:
                releases.append({'version': version, 'details': details})
        return releases


def main():
    urls = {
        "macro": "https://www.jitbit.com/macro-recorder/versionhistory/",
        "helpdesk": "https://www.jitbit.com/helpdesk/versionhistory/"
    }

    scraper = HelpdeskAndMacroScraper(urls)
    scraper.run()

    # Вивід перших кількох версій
    for category, items in scraper.result.items():
        print(f"\n=== {category.upper()} ===")
        for item in items[:3]:
            print(f"{item['version']}:")
            if isinstance(item['details'], list):
                for line in item['details']:
                    print(f"  • {line}")
            else:
                print(f"  {item['details']}")
            print('-' * 60)


if __name__ == "__main__":
    main()
