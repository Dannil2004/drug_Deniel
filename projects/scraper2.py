import requests
from bs4 import BeautifulSoup
import json
import csv
import re


class HelperScraper:
    def __init__(self,url):
        self.url = url

    def fetch_html(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return response.text
        return None
    
    def parse_html(self,html):
        return BeautifulSoup(html,'html.parser')
    
    def save_to_json(self,data,filename):
        with open(filename,'w',encoding='utf-8') as file:
            json.dump(data,file,ensure_ascii=False,indent=4)

    


def save_to_csv(self,data,filename):
    with open(filename,'w',newline='',encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([['Product Name'],["Version"],"Release Date"])
        for item in data:
            writer.writerow({
                item['product'],
                item['version'],
                item['release_date']
            })


class JitBitScraper:
    def __init__(self,url):
        # self.product_name = product_name
        self.data = []
        if isinstance(url, list) or isinstance(url,dict):
            self.urls = url
        else:
            self.url = url
    
    def scrape(self):
     for url in self.urls:
        helper = HelperScraper(url)
        html = helper.fetch_html()
        soup = helper.parse_html(html)
        for h2 in soup.find_all("h2"):
          prod_version = h2.text.strip()
          release_date = h2.find_next("p", class_="text-gray-400").text.strip()
         
          match = re.match(r'(.+?)\s+(\d[\d\.]*)',prod_version)
          print(match.group(1))
          print(match.group(2))

          product = match.group(1)
          version = match.group(2)
     
          
        self.data.append({
         'product' :product,
         'version' : prod_version,
         'release.date' : release_date
           })
        


        helper.save_to_json(self.data,f'eol.json')
if __name__ == "__main__":
    url = ["https://www.jitbit.com/helpdesk/versionhistory/"]
    scraper = JitBitScraper(url)
    scraper.scrape()
            




    
        