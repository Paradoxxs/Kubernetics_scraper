from bs4 import BeautifulSoup, SoupStrainer
import requests
import sqlite3
import time


domain = "https://www.shellsec.pw/"
file = "shellsec.pw\Threads.txt"
database = "shellsec.pw\shellsec.db"

# Read file full of urls 
def read_file(file):
    with open(file,"r") as f:
        urls = f.read().splitlines()
    return urls

Threads = read_file(file)

# Create table
with sqlite3.connect(database) as conn:
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (author TEXT, body TEXT, timestamp TEXT, url TEXT)''')

# Create session
with requests.Session() as session:
    # Parse only part of the document
    parse_only = SoupStrainer(['span', 'div', 'td'])
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    for Thread in Threads:

        print("Scraping: " + Thread)
        page = 1
        while True: # keep looping until there are no more pages
            current_url = f"{domain}{Thread}?page={page}"
            print(current_url)
            cursor.execute("SELECT COUNT(*) FROM posts WHERE url = ?", (current_url,))
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"Already visited {current_url}, skipping.")
                break
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
                conn.commit()

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
           



conn.close()
print("Done!")
