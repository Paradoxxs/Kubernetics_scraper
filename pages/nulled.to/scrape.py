import requests
import time
import random
from bs4 import BeautifulSoup
import re
from requests_html import HTMLSession
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import os


#Vars
source = "nulled.to"
topics = []
processed_urls = set()
es_index = "scraped_nulled"

# User agents and pages to scrape
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36',
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
]

pages = [
    "https://www.nulled.to/#!Home",
    "https://www.nulled.to/#!Pentesting",
    "https://www.nulled.to/#!Leaks",
    "https://www.nulled.to/#!Coding",
    "https://www.nulled.to/#!Monetizing",
    "https://www.nulled.to/#!Marketplace"
]


# Initialize session
session = HTMLSession()

# Get Elasticsearch credentials from environment variables
username = os.getenv('ELASTIC_USER', 'elastic')
password = os.getenv('ELASTIC_PASSWORD', 'changeme')  # Use a default or handle it differently
ca_certs = os.getenv('ELASTICSEARCH_SSL_CERT', None)
es_host = os.getenv('ELASTICSEARCH_HOSTS', 'elasticsearch')
try:
    es = Elasticsearch(
        [{'scheme': 'https', 'host': 'es01', 'port': 9200}],
        basic_auth=(username, password),
        verify_certs=True,
        ca_certs=ca_certs
    )
    if not es.ping():
        raise ValueError("Connection failed")
except Exception as e:
    print("Error connecting to Elasticsearch:", e)
    exit()


def save_to_db(data):
    if data['url'] not in processed_urls:
        doc_id = f"{data['url']}_{data['user_id']}_{data['timestamp']}"
        try:
            es.update(index=es_index, id=doc_id, body={"doc": data, "doc_as_upsert": True})
            processed_urls.add(data['url'])
        except Exception as e:
            print("Error indexing data:", e)
    else:
        print(f"Data with URL {data['url']} already processed")

def scrape_forums(url):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')


        if "Just a moment..." in soup.title.text:
            print("Cloudflare detected, stopping")
            return
        
        all_links = soup.find_all("a")
        pattern = re.compile(r".*/forum/.*")
        for link in all_links:
            href = link.get("href")
            if href and pattern.match(href):
                topics.append(href)
    except Exception as e:
        print("Error scraping forums:", e)

def scrape_posts(soup):
    posts = soup.find_all("tr", class_="__topic")
    for post in posts:
        try:
            url = post.find("td", class_="col_f_content").find("a").get("href")
            title = post.find("td", class_="col_f_content").find("a").text.strip().split("\n")[0]
            author = post.find("td", class_="col_f_content").find("a", class_="url").text.strip()
            user_id = post.find("td", class_="col_f_content").find("a", class_="url").get("href").split("/")[-1]
            timestamp = post.find("td", class_="col_f_content").find("a", class_="topic_title highlight_unread").get("title").split("started")[-1].strip()
            
            if "Today" in timestamp:
                timestamp = datetime.now().strftime("%d %B %Y")
            elif "Yesterday" in timestamp:
                timestamp = (datetime.now() - timedelta(1)).strftime("%d %B %Y")
            else:
                timestamp = timestamp.replace("-", "")
            
            save_to_db({"source": source,"url": url, "title": title, "user_id": user_id, "author": author, "timestamp": timestamp})
            print(f"Inserted {url}")
        except Exception as e:
            print("Error scraping posts:", e)

def scrape_topics(page):
    user_agent = random.choice(user_agents)
    headers = {'User-Agent': user_agent}
    try:
        response = session.get(page, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        scrape_posts(soup)
    except Exception as e:
        print("Possible Cloudflare or scraping error:", e)

print("Starting scraping")

for page in pages:
    print(f"Scraping page: {page}")
    scrape_forums(page)


#remove duplicates from topics
topics = list(dict.fromkeys(topics))
for topic in topics:
    print(f"Scraping topic: {topic}")
    scrape_topics(topic)
    time.sleep(5)
