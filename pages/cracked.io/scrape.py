import requests
import time
import random
from bs4 import BeautifulSoup
import re
from requests_html import HTMLSession
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta

# varibles
urls = []
posts = []
source = "cracked.io"
processed_urls = set()
ex_index = "scraped_cracked"

# Initialize session
session = HTMLSession()

# Elasticsearch connection
try:
    es = Elasticsearch([{'scheme': 'http', 'host': 'elasticsearch', 'port': 9200}])
    if not es.ping():
        raise ValueError("Connection failed")
except Exception as e:
    print("Error connecting to Elasticsearch:", e)

# User agents and pages to scrape
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36',
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
]


def save_to_db(data):
        doc_id = f"{data['url']}_{data['user_id']}_{data['timestamp']}"
        try:
            es.update(index=ex_index, id=doc_id, body={"doc": data, "doc_as_upsert": True})
            
        except Exception as e:
            print("Error indexing data:", e)

def scrape_forums(url):
    print("Starting scraping")
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    if "Just a moment..." in soup.title.text:
        print("Cloudflare detected, stopping")
        return
    
    all_links = soup.find_all("a")
    pattern = re.compile(r".*Forum-.*")

    # Filter and print the links that match the pattern
    for link in all_links:
        href = link.get("href")
        if href and pattern.match(href):
            urls.append(href)




def scrape_topics(url):
    print(f"scraping for posts: {url}")
    archive_url = f"https://cracked.io/{url}"
    user_agent = random.choice(user_agents) 
    headers = {'User-Agent': user_agent}
    response = requests.get(archive_url,headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    elements = soup.find_all("tr", class_="inline_row")
    for element in elements:
        try:
            topic_url = element.find("span", class_="subject_new").find("a").get("href")
            title = element.find("span", class_="subject_new").text.strip()
            posts.append([topic_url, title])
        except:
            continue






def scrape_post(post):
    if post[0] not in processed_urls:
        print(f"scraping comments: {post[0]}")
        archive_url = f"https://cracked.io/{post[0]}"
        user_agent = random.choice(user_agents) 
        headers = {'User-Agent': user_agent}
        response = requests.get(archive_url,headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        comments = soup.find_all("div", class_="post-box")
        for comment in comments:
            try:
    
                user_id = comment.find("div", class_="post-username").find("a").get("href").split("/")[-1]

                author = comment.find("div", class_="post-username").text.strip()
                body = comment.find("div", class_="post_body").text.strip()
                timestamp = comment.find("span", class_="post_date").text.strip()

                save_to_db({"source": source, "url": post[0], "title": post[1], "user_id": user_id, "author": author, "body": body, "timestamp": timestamp})
                print(f"Inserted {post[0]} {user_id}")
            except Exception as e:
                print(e)
                continue
        processed_urls.add(post[0])
    else:
        print(f"URL {post[0]} already processed")


scrape_forums("https://cracked.io/")

#remove urls dublicates
urls = list(set(urls))
for url in urls:
    scrape_topics(url)


for post in posts:
    scrape_post(post)
