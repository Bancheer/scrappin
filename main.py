import requests
from bs4 import BeautifulSoup
import json

url = "http://quotes.toscrape.com"

quotes_data = []
authors_data = []

def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    quotes_container = soup.find_all('div', class_='quote')
    for quote_container in quotes_container:
        try:
            quote_text = quote_container.find('span', class_='text').get_text()
            tags = [tag.text for tag in quote_container.find_all('a', class_='tag')]
            author = quote_container.find('small', class_='author').text
            author_link = "http://quotes.toscrape.com" + quote_container.find('a')['href']
            
            if not any(a['fullname'] == author for a in authors_data):
                try:
                    author_info = scrape_author_info(author_link)
                    authors_data.append(author_info)
                except Exception as e:
                    print(f"Failed to scrape author info for {author}: {str(e)}")
                    continue

            quotes_data.append({
                "quote": quote_text,
                "tags": tags,
                "author": author
            })
        except Exception as e:
            print(f"Error processing quote: {str(e)}")
            continue

def scrape_author_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    fullname_elem = soup.find('h3', class_='author-title')
    born_date_elem = soup.find('span', class_='author-born-date')
    born_location_elem = soup.find('span', class_='author-born-location')
    description_elem = soup.find('div', class_='author-description')

    fullname = fullname_elem.get_text().strip() if fullname_elem else 'N/A'
    born_date = born_date_elem.get_text().strip() if born_date_elem else 'N/A'
    born_location = born_location_elem.get_text().strip() if born_location_elem else 'N/A'
    description = description_elem.get_text().strip() if description_elem else 'N/A'

    return {
        "fullname": fullname,
        "born_date": born_date,
        "born_location": born_location,
        "description": description
    }

while True:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    scrape_page(response.url)
    next_page = soup.find('li', class_='next')
    if next_page:
        url = "http://quotes.toscrape.com" + next_page.find('a')['href']
    else:
        break

with open('quotes.json', 'w', encoding='utf-8') as quotes_file:
    quotes_json = []
    for quote_data in quotes_data:
        quote_json = {
            "tags": quote_data["tags"],
            "author": quote_data["author"],
            "quote": quote_data["quote"]
        }
        quotes_json.append(quote_json)
    
    json.dump(quotes_json, quotes_file, ensure_ascii=False, indent=2)

with open('authors.json', 'w', encoding='utf-8') as authors_file:
    json.dump(authors_data, authors_file, ensure_ascii=False, indent=2)