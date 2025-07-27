# Import required libraries
import requests                    # For sending HTTP requests
from bs4 import BeautifulSoup     # For parsing and navigating HTML content
import json                       # For saving scraped data in JSON format


# Helper class for common scraping operations
class HelperScraper:
    # Fetches the HTML content of a given URL
    def fetch_html(self, url):
        headers = {'User-Agent': 'Mozilla/5.0'}  # Mimic a browser request
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text  # Return the HTML if the request is successful
        return None  # Return None if the request fails

    # Parses raw HTML using BeautifulSoup and returns a soup object 
    def parse_html(self, html):
        return BeautifulSoup(html, 'html.parser')

    # Saves the given data to a JSON file
    def save_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


# Scraper class for extracting Hitachi EOL data from Park Place Technologies
class HitachiScraper:
    def __init__(self):
        # Target URL containing the EOL data for Hitachi products
        self.url = 'https://www.parkplacetechnologies.com/eosl/hitachi/'
        self.data = []  # Initialize an empty list to store scraped results

    # Main method that performs the scraping process
    def scrape(self):
        helper = HelperScraper()                   # Create an instance of the helper class
        html = helper.fetch_html(self.url)         # Fetch HTML content from the URL
        if html is None:
            print("Failed to retrieve page.")
            return

        soup = helper.parse_html(html)             # Parse the HTML content

        # Find the first table on the page (which contains the data)
        table = soup.find('table')
        if not table:
            print('Table not found')               # Display error if table is missing
            return

        # Get all rows from the table except the header row
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')              # Extract all columns from the row
            if len(cols) >= 2:                     # Ensure there are at least two columns
                # Extract model name and EOL date from the columns
                model = cols[0].text.strip()
                eol_date = cols[1].text.strip()

                # Add the extracted data to the list
                self.data.append({
                    'Model': model,
                    'Eol_date': eol_date
                })

        # Save the final data into a JSON file
        helper.save_to_json(self.data, 'hitachi.json')
        print(f'Saved {len(self.data)} entries to hitachi.json')


# Entry point for the script
def main():
    scraper = HitachiScraper()  # Create an instance of the scraper
    scraper.scrape()            # Start the scraping process


# Run the main function if the script is executed directly
if __name__ == '__main__':
    main()
