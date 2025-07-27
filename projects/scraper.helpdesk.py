# Import necessary libraries
import requests                    # Used to send HTTP requests to the target website
from bs4 import BeautifulSoup     # Used for parsing HTML content
import json                       # Used for saving data in JSON format

# Helper class that contains utility functions for web scraping
class HelperScraper:
    # Fetches the HTML content of the given URL
    def fetch_html(self, url):
        headers = {'User-Agent': 'Mozilla/5.0'}  # Set headers to mimic a browser request
        response = requests.get(url, headers=headers)  # Send HTTP GET request
        if response.status_code == 200:                # Check if the request was successful
            return response.text                       # Return HTML content as string

    # Parses the raw HTML using BeautifulSoup and returns a parsed object
    def parse_html(self, html):
        return BeautifulSoup(html, 'html.parser')      # Use the built-in HTML parser

    # Saves extracted data to a JSON file
    def save_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)  # Write formatted JSON

# Main scraper class specifically for Hitachi EOL data
class HitachiScraper:
    def __init__(self):
        # URL of the page that contains End-of-Life information for Hitachi products
        self.url = 'https://www.parkplacetechnologies.com/eosl/hitachi/'
        self.data = []  # Initialize an empty list to store the extracted product data

    # Main method to perform the scraping task
    def scrape(self):
        helper = HelperScraper()                    # Create instance of helper class
        html = helper.fetch_html(self.url)          # Fetch HTML from the target URL
        soup = helper.parse_html(html)              # Parse the HTML content

        table = soup.find('table')                  # Find the first <table> element
        if not table:
            print('Table not found')                # Print error if table is missing
            return

        rows = table.find_all('tr')[1:]             # Get all rows except the header row
        for row in rows:
            cols = row.find_all('td')               # Find all cells in the current row
            if len(cols) >= 2:                      # Ensure at least two columns exist
                model = cols[0].text.strip()        # Extract and clean the model name
                eol_date = cols[1].text.strip()     # Extract and clean the EOL date

                # Append the extracted data as a dictionary to the list
                self.data.append({
                    'Model': model,
                    'Eol_date': eol_date
                })

        # Save the scraped data into a JSON file
        helper.save_to_json(self.data, 'hitachi.json')
        print(f'Saved {len(self.data)} entries to hitachi.json')  # Output the result

# Function to run the scraper
def main():
    scraper = HitachiScraper()  # Create a scraper instance
    scraper.scrape()            # Start the scraping process

# Ensures that main() runs only when this script is executed directly
if __name__ == '__main__':
    main()
