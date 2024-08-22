import requests
from bs4 import BeautifulSoup
import random

def is_techzone_url(url):
    """Check if the URL contains 'https://ayoubcomputers.com/'."""
    return "https://techzone.com.lb/" in url

def make_request(site):
    """Make a GET request to the given URL using a randomly selected proxy from the file."""
    try:
        # Load proxies from file
        with open("valid_proxy.txt") as f:
            proxies = f.read().splitlines()

        # Select a random proxy
        proxy = random.choice(proxies)
        proxy_dict = {'http': proxy}
        print(f"Using the proxy: {proxy}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Make the request
        response = requests.get(site, proxies=proxy_dict, headers=headers, timeout=10)
        response.raise_for_status()  # Check if the request was successful
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def fetch_data(response):
    """Fetch the title and price from the HTML response."""
    if response:
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the title
        title = soup.find("h1", class_="product_title entry-title wd-entities-title")
        if title:
            print("Title:", title.get_text(strip=True))
        else:
            print("Title not found.")

        # Find the price
        price=soup.find('p', class_='price').find('span', class_='woocommerce-Price-amount')
        if price:
            print("Price:", price.get_text(strip=True))
        else:
            print("Price not found.")
    else:
        print("No response to fetch data from.")

def main():
    site_to_check = [
       "https://techzone.com.lb/product/tt-toughpower-gf3-1000w-80-plus-gold-atx3-0-gen5-connector/"
    ]
    
    for site in site_to_check:
            if is_techzone_url(site):
                print(f"Processing URL: {site}")
                response = make_request(site)
                fetch_data(response)
            else:
                print(f"Skipping URL: {site} (Not an techzone.com URL)")

if __name__ == "__main__":
    main()
