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

def ayoub(response):
    """Fetch the title and price from the HTML response."""
    if response:
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the title
        title = soup.find("h1", class_="productView-title")
        if title:
            print("Title:", title.get_text(strip=True))
        else:
            print("Title not found.")

        # Find the price
        price = soup.find("span", class_="price price--withoutTax price--main")
        if price:
            print("Price:", price.get_text(strip=True))
        else:
            print("Price not found.")
    else:
        print("No response to fetch data from.")

def main():
    site_to_check = [
        "https://ayoubcomputers.com/lenovo-ideapad-1-15iau7-15-6-laptop-intel-core-i3-1215u-ram-4gb-ssd-256gb-intel-uhd-win-11-82qd008hax/",
        "https://ayoubcomputers.com/alienware-vindicator-2-0-neoprene-17-gaming-laptop-bag-black-awv17ns2-0/",
        "https://ayoubcomputers.com/apple-macbook-air-13-laptop-apple-m3-with-8-core-chip-ram-16gb-ssd-512gb-10-core-gpu-starlight-mxcu3/",
        "https://books.toscrape.com/catalogue/category/books/fantasy_19/index.html"
    ]
    

    for site in site_to_check:
        if is_ayoubcomputers_url(site):
            print(f"Processing URL: {site}")
            response = make_request(site)
            fetch_data(response)
        else:
            print(f"Skipping URL: {site} (Not an ayoubcomputers.com URL)")

if __name__ == "__main__":
    main()
