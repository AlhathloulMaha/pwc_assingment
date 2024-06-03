import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

class WebScraper:
    def __init__(self):
        pass

    def get_all_links(self, url, visited=None, link_attempts=None, depth=3, max_attempts=5, exclude_patterns=None):
        if visited is None:
            visited = set()
        if link_attempts is None:
            link_attempts = {}
        if exclude_patterns is None:
            exclude_patterns = []

        if depth == 0:
            return []

        links = []

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to retrieve {url}: {e}")
            return links

        soup = BeautifulSoup(response.content, 'html.parser')
        base_url = urllib.parse.urlparse(url).scheme + '://' + urllib.parse.urlparse(url).netloc

        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and not href.startswith('#'):
                full_url = urllib.parse.urljoin(base_url, href)
                parsed_url = urllib.parse.urlparse(full_url)

                if parsed_url.scheme + '://' + parsed_url.netloc == base_url and parsed_url.path.startswith(urllib.parse.urlparse(url).path):
                    if any(pattern in full_url for pattern in exclude_patterns):
                        print(f"Excluding link: {full_url}")
                        continue

                    if full_url in link_attempts:
                        link_attempts[full_url] += 1
                    else:
                        link_attempts[full_url] = 1

                    if link_attempts[full_url] > max_attempts:
                        print(f"Skipping {full_url} after {max_attempts} attempts.")
                        continue

                    visited.add(full_url)
                    links.append(full_url)
                    print(f"Found link: {full_url}")
                    time.sleep(1)
                    links += self.get_all_links(full_url, visited, link_attempts, depth-1, max_attempts, exclude_patterns)  

        return links  

    def fetch_webpage(self, url, retries=3, timeout=5):
        for i in range(retries):
            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                return response.content
            except (requests.ConnectionError, requests.Timeout) as e:
                print(f"Attempt {i + 1} failed with error: {e}")
                time.sleep(2 ** i)
        raise Exception(f"Failed to retrieve the webpage after {retries} attempts")

    def scrape_and_save(self, url):
        try:
            webpage_content = self.fetch_webpage(url)
            soup = BeautifulSoup(webpage_content, 'html.parser')
            paragraphs = soup.find_all('p')
            data = [p.get_text() for p in paragraphs]

            with open('output.txt', 'a') as f:
                f.write("Paragraphs:\n")
                for paragraph in data:
                    f.write(paragraph + '\n')

            print("Data scraped and saved successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    scraper = WebScraper()
    start_url = 'https://u.ae/en/information-and-services'  
    exclude_patterns = ['readspeaker', 'another-pattern'] 
    all_links = scraper.get_all_links(start_url, exclude_patterns=exclude_patterns)
    print(f"Total links found: {len(all_links)}")
    print("All links:", all_links)
    
    for url in all_links:
        scraper.scrape_and_save(url)
