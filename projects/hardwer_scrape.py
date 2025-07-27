# Import required libraries
import requests                    # For sending HTTP requests
from bs4 import BeautifulSoup     # For parsing HTML content
import json                       # For saving data in JSON format


# Helper class for fetching, parsing, and saving data
class HelperScraper:
    # Fetches the HTML content of a given URL
    def fetch_html(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  # Return HTML content if request is successful
        return None               # Return None if request fails

    # Parses raw HTML using BeautifulSoup and returns a soup object
    def parse_html(self, html):
        return BeautifulSoup(html, 'html.parser')

    # Saves the given data to a JSON file
    def save_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


# Scraper class for extracting EOL data from hardwarewartung.com
class HardwareScraper:
    def __init__(self):
        # Target URL that contains Hitachi EOL product data
        self.base_url = 'https://www.hardwarewartung.com/en/hitachi-end-of-life-en/'
        self.data = []  # List to store the extracted data

    # Main method that performs the scraping process
    def scrape(self):
        helper = HelperScraper()                      # Create a helper instance
        html = helper.fetch_html(self.base_url)       # Fetch the HTML content
        if html is None:
            print("Failed to fetch the webpage.")
            return

        soup = helper.parse_html(html)                # Parse the HTML

        table = soup.find('table')                    # Find the first table on the page
        if not table:
            print("Table not found on the page.")     # If no table found, print message
            return

        rows = table.find_all('tr')[1:]               # Skip the table header

        for row in rows:
            cols = row.find_all("td")                 # Get all columns in the row
            if len(cols) > 3:                         # Ensure there are enough columns
                product_name = cols[0].text.strip()
                model = cols[1].text.strip()
                eol_date = cols[2].text.strip()
                support_date = cols[3].text.strip()

                # Append the extracted data to the list
                self.data.append({
                    'manufacturer': product_name,
                    'model': model,
                    'end_of_service_life': eol_date,
                    'support_until': support_date
                })

        # Save all data to a JSON file
        helper.save_to_json(self.data, 'hardware.json')
        print(f"Saved {len(self.data)} records to hardware.json")


# Entry point for the script
def main():
    scraper = HardwareScraper()  # Create scraper instance
    scraper.scrape()             # Start scraping


# Execute the script only if run directly
if __name__ == '__main__':
    main()











       



    
