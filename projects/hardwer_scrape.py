import requests
from bs4 import BeautifulSoup
import json

class HelperScraper:
    def fetch_html(self,url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        

    def parse_html(self,html):
        return BeautifulSoup(html,'html.parser')
    

    def save_to_json(self,data,filname):
        with open(filname,'w',encoding='utf-8') as file:
            json.dump(data,file,ensure_ascii=False,indent=4)


class HardwerScraper:
    def __init__(self):
        self.base_url = 'https://www.hardwarewartung.com/en/hitachi-end-of-life-en/'
        self.data = []

    def scrape(self):
        helper = HelperScraper()
        html = helper.fetch_html(self.base_url)
        soup = helper.parse_html(html)

        table = soup.find('table')
        if not table:
            return print("Nima")
        
        rows = table.find_all('tr')[1:]

        for row in rows:
            cols = row.find_all("td")
            if len(cols)>3:
                product_name = cols[0].text.strip()
                model = cols[1].text.strip()
                eol_data = cols[2].text.strip()
                support_data = cols[3].text.strip()

                self.data.append({
                    'Manuf' : product_name,
                    'model' : model,
                    'end_of_servise_life' : eol_data,
                    'support_till' : support_data
                })

        helper.save_to_json(self.data,'hardwer.json')
        print(f"Saved {len(self.data)} in hardwer.json")


def main():
     scraper = HardwerScraper()
     scraper.scrape()


if __name__ == '__main__':
    main()











       



    