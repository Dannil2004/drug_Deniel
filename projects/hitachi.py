import requests
from bs4 import BeautifulSoup
import json

# Helper class for common scraping operations
class HelperScraper:
     # Fetches the HTML content of a given URL
    def fetch_html(self,url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        # Parses raw HTML using BeautifulSoup and returns a soup object 
    def parse_html(self,html):
        return BeautifulSoup(html,'html.parser')
    # Saves the given data to a JSON file
    def save_to_json(self,data,filname):
        with open(filname,'w',encoding='utf-8') as file:
            json.dump(data,file,ensure_ascii=False,indent=4)

# Scraper class for extracting Hitachi EOL data from Park Place Technologies
class HitachiScraper:
    def __init__(self):
        self.url = 'https://www.parkplacetechnologies.com/eosl/hitachi/'
        self.data = []

    # Main method that performs the scraping process
    def scrape(self):
        helper = HelperScraper()
        html  = helper.fetch_html(self.url)
        soup = helper.parse_html(html)
        # Find the first table on the page (which contains the data)
        table = soup.find('table')
        if not table:
            print('table not find')
            return
         # Get all rows from the table except the header
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols)>=2:
                # Extract model and EOL date from the columns
                model = cols[0].text.strip()
                eol_date = cols[1].text.strip()
 # Add the extracted data to the list
                self.data.append({
                    'Model': model,
                    'Eol_date' : eol_date
                })
  # Save the final data into a JSON file
        helper.save_to_json(self.data,'hitachi.json')
        print(f'Saved{len(self.data)} in hitachi.json')
# Entry point for the script
def main():
    scraper = HitachiScraper()
    scraper.scrape()
# Run the main function if the script is executed directly
if __name__ == '__main__':
    main()
