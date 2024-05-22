import time
import random
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

# Set up Undetected ChromeDriver
options = uc.ChromeOptions()
options.headless = True
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')
options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"  # Update this path if necessary

driver = uc.Chrome(options=options)

# Base URL of the forum
BASE_URL = 'https://patched.to'

forums = [
    "Forum-personal-life", "Forum-achievements-bragging", "Forum-gaming", "Forum-entertainment", 
    "Forum-crypto-currencies", "Forum-the-lounge", "Forum-cracking-tools", "Forum-cracking-tutorials", 
    "Forum-configs", "Forum-proxies", "Forum-combolist", "Forum-cracked-programs", "Forum-accounts", 
    "Forum-tutorials-guides-ebooks-etc", "Forum-source-codes", "Forum-requests", "Forum-other-leaks", 
    "Forum-net-framework", "Forum-html-css-js-php", "Forum-c-c", "Forum-other-languages", "Forum-general", 
    "Forum-reverse-engineering-guides-and-tips", "Forum-tools", "Forum-monetizing-techniques", 
    "Forum-social-engineering", "Forum-e-whoring", "Forum-real-life-businesses", "Forum-cryptocoins", 
    "Forum-marketplace-lobby", "Forum-secondary-sellers", "Forum-buyers", "Forum-trading-station", 
    "Forum-service-requests"
]

# Function to scrape a single forum page
def scrape_forum_page(url):
    driver.get(url)
    time.sleep(random.uniform(5, 10))  # Wait for page to load completely and for Cloudflare checks

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print(soup)
    # Example: scraping thread titles and links
    threads = soup.find_all('a', class_='thread_title')
    print(threads)
    for thread in threads:
        title = thread.text.strip()
        link = BASE_URL + thread['href']
        print(f'Title: {title}, Link: {link}')

    # Find the next page link if it exists
    next_page = soup.find('a', class_='next')
    if next_page and 'href' in next_page.attrs:
        next_page_url = BASE_URL + next_page['href']
        return next_page_url
    return None

# Scrape all pages in the forum
def scrape_all_forum_pages(start_url):
    next_url = start_url
    while next_url:
        print(f'Scraping page: {next_url}')
        next_url = scrape_forum_page(next_url)
        time.sleep(random.uniform(3, 7))  # Add delay between requests

# Start scraping from the first forum page
for forum in forums:
    url = f'{BASE_URL}/{forum}'
    print(f'Starting to scrape forum: {url}')
    scrape_forum_page(url)

driver.quit()
