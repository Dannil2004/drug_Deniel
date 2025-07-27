# Import required libraries
import requests                    # For sending HTTP requests
from bs4 import BeautifulSoup     # For parsing HTML content
import json                       # For saving data in JSON format


# Helper class to handle common tasks like fetching, parsing, and saving data
class ScraperHelper:
    # Fetches the HTML content of the given URL
    def fetch_html(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  # Return the HTML content if successful
        return None               # Return None if the request fails

    # Parses the raw HTML content and returns a BeautifulSoup object
    def parse_html(self, html):
        return BeautifulSoup(html, 'html.parser')

    # Saves the provided data to a JSON file
    def save_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# Scraper class for Adobe's End-of-Life (EOL) product matrix page
class AdobeScraper:
    def __init__(self):
        # Target URL for Adobe product EOL information
        self.base_url = 'https://helpx.adobe.com/support/programs/eol-matrix.html'
        self.data = []  # List to store extracted product data

    # Method to perform the scraping
    def scrape(self):
        helper = ScraperHelper()
        html = helper.fetch_html(self.base_url)  # Fetch HTML content

        if html is None:
            print("Failed to fetch the page.")
            return

        soup = helper.parse_html(html)           # Parse the HTML

        table = soup.find("table")               # Find the first <table> on the page
        if not table:
            print("Table not found")
            return

        rows = table.find_all("tr")[1:]          # Skip the table header

        for row in rows:
            cols = row.find_all('td')            # Extract all columns in the row
            if len(cols) >= 6:
                # Extract and clean the text from each relevant column
                product_name = cols[0].text.strip()
                version = cols[1].text.strip()
                build = cols[2].text.strip()
                general_availability = cols[3].text.strip()
                end_of_core_support = cols[4].text.strip()
                end_of_extended_support = cols[5].text.strip()

                # Append the data to the list as a dictionary
                self.data.append({
                    'product_name': product_name,
                    'version': version,
                    'build': build,
                    'general_availability': general_availability,
                    'end_of_core_support': end_of_core_support,
                    'end_of_extended_support': end_of_extended_support
                })

        # Save the collected data to a JSON file
        helper.save_to_json(self.data, 'all_products.json')
        print(f"Saved {len(self.data)} entries to all_products.json")


# Entry point function
def main():
    scraper = AdobeScraper()  # Create an instance of the scraper
    scraper.scrape()          # Run the scraping logic


# Run the script if executed directly
if __name__ == '__main__':
    main()

