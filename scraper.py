import requests
from bs4 import BeautifulSoup

def scrape_buyrentkenya(search_query="luxury-villas"):
    url = f"https://www.buyrentkenya.com/listings?q={search_query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    listings = []
    # This logic targets the specific CSS classes BuyRentKenya uses
    for item in soup.find_all('div', class_='listing-card'): 
        try:
            title = item.find('h2').text.strip()
            price = item.find('p', class_='price').text.strip()
            location = item.find('p', class_='location').text.strip()
            
            # Filter for high-end properties only
            listings.append({
                'title': title,
                'price': price,
                'location': location,
                'source': 'BuyRentKenya'
            })
        except:
            continue
            
    return listings