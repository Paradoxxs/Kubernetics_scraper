from bs4 import BeautifulSoup, SoupStrainer
import requests
import time
import requests
import time
import random
from elasticsearch import Elasticsearch
import os


source = "shellsec"
es_index = "scraped_"+ source
domain = "https://www.shellsec.pw/"
Threads = []
processed_urls = set()

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36',
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
]

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
        doc_id = f"{data['url']}_{data['user_id']}_{data['timestamp']}"
        try:
            es.update(index=es_index, id=doc_id, body={"doc": data, "doc_as_upsert": True})
            print("Inserting data: " + data['url'])
        except Exception as e:
            print("Error indexing data:", e)


def get_category_links(session):
    url = f"{domain}/index.php"
    response = session.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    links = [domain + link['href'] for forum_row in soup.find_all('tr') 
             for link in forum_row.find_all('a') if link['href'].startswith('forum-')]
    return links

def get_category_sides(session, url):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    threads = get_all_threads(soup)
    return threads

"""     pagination_section = soup.find('div', {'class': 'pagination'})
    if pagination_section is not None:
        last_page_link = pagination_section.find('a', {'class': 'pagination_last'})
        if last_page_link is not None:
            last_page_number = int(last_page_link.text)
            for page_number in range(2, last_page_number+1):
                page_url = url+f"/?page={page_number}"
                response = session.get(page_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                threads += get_all_threads(soup)
        else:
            threads += [get_all_threads(BeautifulSoup(session.get(domain + page_link["href"]).text, 'html.parser')) 
                        for page_link in pagination_section.find_all('a', {'class': 'pagination_page'})]
    return threads """

def get_all_threads(soup):
    return [link['href'].split('?')[0] for threads in soup.find_all('tr') 
            for link in threads.find_all('a') if link['href'].startswith('traad-')]

with requests.Session() as session:
    category_links = get_category_links(session)
    for category_link in category_links:
        Threads += get_category_sides(session, category_link)



def get_posts():
    # Create session
    with requests.Session() as session:
        # Parse only part of the document
        parse_only = SoupStrainer(['span', 'div', 'td'])
        
        for Thread in Threads:
            try:
                user_agent = random.choice(user_agents)
                headers = {'User-Agent': user_agent}

                print("Scraping for posts: " + Thread)
                current_url = f"{domain}{Thread}?page=1"

                response = session.get(current_url,headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser', parse_only=parse_only)

                # Find all tables with class "tborder"
                tables = soup.find_all(lambda tag: tag.name == 'table' and tag.get('class') == ['tborder'] and tag.has_attr('id'))

                for table in tables:
                    timestamp_div = table.find('div', {'class': 'float_left smalltext'})
                    if timestamp_div:
                        timestamp = timestamp_div.text.strip().split(' ')[0:2]
                        timestamp = ' '.join(timestamp)

                    # Find author
                    author_div = table.find('span',{'class': 'largetext'})
                    if author_div:
                        author = author_div.text.strip()


                    # Find post body
                    body_div = table.find('div', {'class': 'post_body'})
                    if body_div:
                        body = body_div.text.strip()

                    save_to_db({"source": source, "url": current_url, "user_id": author, "timestamp": timestamp, "author": author, "body": body})
            except:
                print("Error scraping: " + Thread)
                pass
            processed_urls.add(Thread)


def get_all_posts():
    # Create session
    with requests.Session() as session:
        # Parse only part of the document
        parse_only = SoupStrainer(['span', 'div', 'td'])
        
        for Thread in Threads:
            
            print("Scraping for posts: " + Thread)
            page = 1
            while True: # keep looping until there are no more pages
                current_url = f"{domain}{Thread}?page={page}"
                print(current_url)
                time.sleep(10)
                response = session.get(current_url)
                soup = BeautifulSoup(response.text, 'html.parser', parse_only=parse_only)

                # Find all tables with class "tborder"
                tables = soup.find_all(lambda tag: tag.name == 'table' and tag.get('class') == ['tborder'] and tag.has_attr('id'))

                for table in tables:
                    timestamp_div = table.find('div', {'class': 'float_left smalltext'})
                    if timestamp_div:
                        timestamp = timestamp_div.text.strip().split(' ')[0:2]
                        timestamp = ' '.join(timestamp)

                    # Find author
                    author_div = table.find('span',{'class': 'largetext'})
                    if author_div:
                        author = author_div.text.strip()


                    # Find post body
                    body_div = table.find('div', {'class': 'post_body'})
                    if body_div:
                        body = body_div.text.strip()


                    cursor.execute("INSERT INTO posts VALUES (?,?,?,?)", (author, body, timestamp, current_url))

                # Check if there is a next page
                pagination_divs = soup.find_all('div', {'class': 'pagination'})
                if len(pagination_divs) > 1:
                    second_pagination_div = pagination_divs[1]
                    next_page_link = second_pagination_div.find('a', {'class': 'pagination_next'}) if second_pagination_div else None
                    if next_page_link is not None:
                        page += 1
                    else:
                        break
                else:
                    break



get_posts()