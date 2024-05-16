import requests
import time
import random
from bs4 import BeautifulSoup
import re
from requests_html import HTMLSession
from elasticsearch import Elasticsearch

Session = HTMLSession()

# Elasticsearch connection
es = Elasticsearch([{'scheme': 'http','host': 'localhost', 'port': 9200}])

user_agents = [ 
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 
    'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36',
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
]

urls = ["https://www.nulled.to/#!Home","https://www.nulled.to/#!Pentesting","https://www.nulled.to/#!Leaks", "https://www.nulled.to/#!Coding" , "https://www.nulled.to/#!Monetizing", "https://www.nulled.to/#!Marketplace",  ]
pages = []


def save_to_db(data):
    # Index data into Elasticsearch
    es.index(index="scraped_data", doc_type="_doc", body={"data": data})

def scrape_forums(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    all_links = soup.find_all("a")
    pattern = re.compile(r".*/forum/.*")

    # Filter and print the links that match the pattern
    for link in all_links:
        href = link.get("href")
        if href and pattern.match(href):
            pages.append(href)


def scrape_topics(soup):
    #print(soup)
    topics = soup.find_all("tr",class_="__topic")
    for topic in topics:
        try:
            url = topic.find("td",class_="col_f_content").find("a").get("href")
            #print(url)
            title = topic.find("td",class_="col_f_content").find("a").text.strip().split("\n")[0]
            #print(title)
            author = topic.find("td",class_="col_f_content").find("a", class_="url").text.strip()
            #print(author)
            user_id = topic.find("td",class_="col_f_content").find("a", class_="url").get("href").split("/")[-1]
            #print(user_id)
            timestamp = topic.find("td",class_="col_f_content").find("a",class_="topic_title highlight_unread").get("title").split("started")[-1].replace("-","")
            #if timestamp contains word today, replace it with today's date with the following format 28 December 2022
            if "Today" in timestamp:
                timestamp = time.strftime("%d %B %Y")

            if "Yesterday" in timestamp:
                #add yesterday to timestamp
                timestamp = time.strftime("%d-%B-%Y")


            save_to_db([url,title,user_id,author,timestamp])
            print(f"inserted {url}")
        except Exception as e:
            print(e)

def scrape_forum_page(url):
    user_agent = random.choice(user_agents) 
    headers = {'User-Agent': user_agent}
    try:
        response = Session.get(url,headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        scrape_topics(soup)
    except:
        print("Possible cloudflare")


## update the select statement so it only gets the once that have not been scraped before.
for page in pages:
    scrape_forum_page(page)
    time.sleep(5)