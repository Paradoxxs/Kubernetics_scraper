from bs4 import BeautifulSoup
import requests

response = requests.get("https://www.shellsec.pw/forum-generelt-introduktion")

# assuming 'html' is the variable containing your HTML content
soup = BeautifulSoup(response.text, 'html.parser')


# Find pagination section
pagination_section = soup.find('div', {'class': 'pagination'})

# If pagination section is found...
if pagination_section is not None:

    # Find all 'a' elements representing pages in the pagination section
    page_links = pagination_section.find('a', {'class': 'pagination_page'})

    # find last page number
    last_page_link = pagination_section.find('a', {'class': 'pagination_last'})
    
    if last_page_link is not None:
        last_page_number = int(last_page_link.text) 


        for page_number in range(1, last_page_number):
            page_url = page_links+f"/?page={page_number}"
            
            # Make a request to the page URL
            response = requests.get(page_url)

            # Parse the page with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            

    else:   
        # Find all 'a' elements representing pages in the pagination section
        page_links = pagination_section.find('a', {'class': 'pagination_page'})
        
        # For each page link...
        for page_link in page_links:

            # Get the URL of the page
            page_url = page_link['href']
            
            # Make an HTTP request to fetch the HTML of the page
            response = requests.get('https://www.shellsec.pw/' + page_url)

            # Parse the HTML using BeautifulSoup
            page_soup = BeautifulSoup(response.text, 'html.parser')
            
