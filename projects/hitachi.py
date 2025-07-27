import requests
from bs4 import BeautifulSoup
import json

class HelperScraper:
    def fetch_html(self,url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        
    def parse_html(self,html):
        return BeautifulSoup(html,'html.parser')
    
    def save_to_json(self,data,filname):
        with open(filname,'w',encoding='utf-8') as file:
            json.dump(data,file,ensure_ascii=False,indent=4)


class HitachiScraper:
    def __init__(self):
        self.url = 'https://www.parkplacetechnologies.com/eosl/hitachi/'
        self.data = []


    def scrape(self):
        helper = HelperScraper()
        html  = helper.fetch_html(self.url)
        soup = helper.parse_html(html)
        table = soup.find('table')
        if not table:
            print('table not find')
            return
        
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols)>=2:
                model = cols[0].text.strip()
                eol_date = cols[1].text.strip()

                self.data.append({
                    'Model': model,
                    'Eol_date' : eol_date
                })

        helper.save_to_json(self.data,'hitachi.json')
        print(f'Saved{len(self.data)} in hitachi.json')

def main():
    scraper = HitachiScraper()
    scraper.scrape()

if __name__ == '__main__':
    main()
