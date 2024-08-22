import requests
from bs4 import BeautifulSoup
import random

def is_ayoubcomputers_url(url):
    """Check if the URL contains 'https://ayoubcomputers.com/'."""
    return "https://ayoubcomputers.com/" in url

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

def newegg(response):
    """Fetch the title and price from the HTML response."""
    if response:
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the title
        title = soup.find("h1", class_="product-title")
        if title:
            print("Title:", title.get_text(strip=True))
        else:
            print("Title not found.")

        # Find the price
        price_li = soup.find('li', class_='price-current')
        if price_li:
            # Extract the text from the price elements
            dollar_part = price_li.find('strong').get_text(strip=True)
            cents_part = price_li.find('sup').get_text(strip=True)
            price = f"${dollar_part}{cents_part}"
            print("Price:", price)
        else:
            print("Price not found.")

def main():
    site_to_check = [
       "https://www.newegg.com/team-model-tc1863128gb01/p/N82E16820331263?Item=N82E16820331263&cm_sp=Homepage_SS-_-P1_20-331-263-_-08212024",
       "https://www.newegg.com/seagate-firecuda-st4000dx005-4tb-gaming-hard-drives-7200-rpm/p/N82E16822185035?Item=N82E16822185035&cm_sp=Homepage_SS-_-P2_22-185-035-_-08212024"
    ]
    

    for site in site_to_check:
        
            response = make_request(site)
            fetch_data(response)
        

if __name__ == "__main__":
    main()
