from bs4 import BeautifulSoup
import requests

domain = "https://www.shellsec.pw/"

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

    pagination_section = soup.find('div', {'class': 'pagination'})
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
    return threads

def get_all_threads(soup):
    return [link['href'].split('?')[0] for threads in soup.find_all('tr') 
            for link in threads.find_all('a') if link['href'].startswith('traad-')]

with requests.Session() as session:
    category_links = get_category_links(session)
    threads = []
    for category_link in category_links:
        threads += get_category_sides(session, category_link)
    threads = list(set(threads))  # Remove duplicates

    text = '\n'.join(threads)
    with open('Threads.txt', 'w') as f:
        f.write(text)
