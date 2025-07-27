# Import required libraries
import requests                    # For making HTTP requests
from bs4 import BeautifulSoup     # For parsing HTML content
import json                       # For saving data in JSON format
import csv                        # For writing data to CSV files
import re                         # For regular expression matching
  

# Helper class to fetch and parse HTML, and save data
class HelperScraper:
    def __init__(self, url):
        self.url = url  # Store the URL for the current scraping task

    # Fetch the raw HTML content of the page
    def fetch_html(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return response.text  # Return HTML content if the request is successful
        return None  # Return None if the request failed

    # Parse HTML using BeautifulSoup and return a soup object
    def parse_html(self, html):
        return BeautifulSoup(html, 'html.parser')

    # Save scraped data to a JSON file
    def save_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    # Save scraped data to a CSV file
    def save_to_csv(self, data, filename):
        with open(filename, 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Product Name", "Version", "Release Date"])  # Write CSV header
            for item in data:
                writer.writerow([
                    item['product'],
                    item['version'],
                    item['release_date']
                ])


# Main scraper class for JitBit Helpdesk version history
class JitBitScraper:
    def __init__(self, url):
        self.data = []  # List to store scraped data

        # Allow either a single URL string or a list of URLs
        if isinstance(url, list) or isinstance(url, dict):
            self.urls = url
        else:
            self.urls = [url]  # Convert single URL to a list

    # Scraping logic
    def scrape(self):
        for url in self.urls:
            helper = HelperScraper(url)       # Create helper instance for each URL
            html = helper.fetch_html()        # Fetch HTML content
            if html is None:
                print(f"Failed to fetch {url}")
                continue
            soup = helper.parse_html(html)    # Parse HTML

            # Loop through all version headers (assumed to be in <h2>)
            for h2 in soup.find_all("h2"):
                prod_version = h2.text.strip()  # Extract full text like "ProductName 10.5"
                # Find the release date in the following paragraph
                p_tag = h2.find_next("p", class_="text-gray-400")
                release_date = p_tag.text.strip() if p_tag else "Unknown"

                # Use regex to separate product name and version number
                match = re.match(r'(.+?)\s+(\d[\d\.]*)', prod_version)
                if match:
                    product = match.group(1)
                    version = match.group(2)

                    # Add the extracted data to the list
                    self.data.append({
                        'product': product,
                        'version': version,
                        'release_date': release_date
                    })

        # Save all scraped data to JSON and CSV
        if self.data:
            helper.save_to_json(self.data, 'jitbit_eol.json')
            helper.save_to_csv(self.data, 'jitbit_eol.csv')
            print(f"Saved {len(self.data)} entries to 'jitbit_eol.json' and 'jitbit_eol.csv'")
        else:
            print("No data found to save.")


# Entry point of the script
if __name__ == "__main__":
    url = ["https://www.jitbit.com/helpdesk/versionhistory/"]  # URL(s) to scrape
    scraper = JitBitScraper(url)  # Create scraper instance
    scraper.scrape()              # Run scraping




    
        
