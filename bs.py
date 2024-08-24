import requests
import random
from bs4 import BeautifulSoup

# > get random proxy from valid proxies.txt
def get_random_proxy(proxy_file):
    with open(proxy_file, "r") as f:
        proxies = [line.strip() for line in f if line.strip()]
    return random.choice(proxies) if proxies else None


def scrape_data(url, proxy_file):
    proxy = get_random_proxy(proxy_file)
    if not proxy:
        print("No valid proxies available.")
        return

    try:
        # > get using proxy
        response = requests.get(
        url,
        proxies={"http": proxy},
        timeout=10
        )

        if response.status_code != 200:
            print(f"Failed to scrape data. Status code: {response.status_code}")

        # > scan using bs4
        soup = BeautifulSoup(response.content, "html.parser")

        element = soup.find('span', class_=['price-item', 'price-item--regular'])
        element = soup.find('span', itemprop='price')
        # product_title = soup.find('div', class_='product__title').find('h1').text

        print(element.text)

    except requests.RequestException as e:
        print(f"Request failed: {e}")



def main():
    url_to_scrape = "https://460estore.com/gaming-keyboard-mouse/6374-hoco-gaming-luminous-wired-mouse.html?gad_source=1&gclid=CjwKCAjwoJa2BhBPEiwA0l0ImET5zvEL495rZ4tYF4LyJU188oTC86MBqijx5k4HrzLHYVsAwcZ32xoCIisQAvD_BwE" 
    proxy_file = "valid_proxies.txt"

    scrape_data(url_to_scrape, proxy_file)

main()
