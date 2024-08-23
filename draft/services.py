import requests
from bs4 import BeautifulSoup
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from flask import jsonify



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





def alibaba(response):
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Initialize default values
       

        # Extract the title
        title = soup.find("h1", title=True)
        if title:
            title_text = title.get_text(strip=True)

        # Extract the price
        price_element = soup.find('div', class_='price')
        if price_element:
            price_text = price_element.get_text(strip=True)
        else:
            # Fallback: Look for the price in span elements
            price_spans = soup.find_all('span')
            for span in price_spans:
                if "$" in span.text:
                    price_text = span.get_text(strip=True)
                    break

        # Create a dictionary to hold the results
        result = {
            "title": title_text,
            "price": price_text
        }

        # Return the result as a JSON object
        return json.dumps(result)
    else:
        return json({"error": "No response"})




def ayoub(response):
    if response:
        soup = BeautifulSoup(response.text, "html.parser")

        # Initialize variables with default values
        title_text1 = "Title not found"
        price_text = "Price not found"

        # Find the title
        title = soup.find("h1", class_="productView-title")
        if title:
            title_text1 = title.get_text(strip=True)

        # Find the price
        price = soup.find("span", class_="price price--withoutTax price--main")
        if price:
            price_text = price.get_text(strip=True)
        
        result = {
            "title": title_text1,
            "price": price_text
        }

        # Return the result as a JSON object
        return json.dumps(result)
    else:
        return json.dumps({"error": "No response"})

       
    


def newegg(response):
    if response:
        soup = BeautifulSoup(response.text, "html.parser")

        # Initialize default values
        title_text = "Title not found"
        price = "Price not found"

        # Find the title
        title = soup.find("h1", class_="product-title")
        if title:
            title_text = title.get_text(strip=True)

        # Find the price
        price_li = soup.find('li', class_='price-current')
        if price_li:
            dollar_part = price_li.find('strong')
            cents_part = price_li.find('sup')

            if dollar_part and cents_part:
                price = f"${dollar_part.get_text(strip=True)}{cents_part.get_text(strip=True)}"
            elif dollar_part:  # Handle cases where cents_part might be missing
                price = f"${dollar_part.get_text(strip=True)}"

        result = {
            "title": title_text,
            "price": price
        }

        # Return the result as a JSON object
        return json.dumps(result)
    else:
        return json.dumps({"error": "No response"})
           


def shein(url):
    # Setup Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        # Navigate to the webpage
        driver.get(url)

        # Extract the title
        title_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-intro__head-name"))
        )
        title = title_element.text

        # Extract the price
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "from.original"))
        )
        price = price_element.text

        # Return the result as a list
        return [title, price]

    finally:
        # Close the driver
        driver.quit()
       
def techzone(response):
    """Fetch the title and price from the HTML response."""
    if response:
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the title
        title = soup.find("h1", class_="product_title entry-title wd-entities-title")
        if title:
           title_text= title.get_text(strip=True)
        

        # Find the price
        price=soup.find('p', class_='price').find('span', class_='woocommerce-Price-amount')
        if price:
            price_text=price.get_text(strip=True)
        result = {
            "title": title_text,
            "price": price_text
        }
        return json.dumps(result)
    else:
        return json.dumps({"error": "No response"})
        
def main():
    site_to_check = [
        "https://ar.shein.com/2023-New-Ultra-Thin-Hard-Shell-Laptop-Case-Compatible-With-Apple-Laptop-Pro-13-A2338-Apple-Laptop-Air-13-A2337-M1-M2-Chip-2022-Apple-Laptop-Air-13-6-A2681-Pro-14-A2442-p-31625154.html?src_identifier=st%3D2%60sc%3Dlaptop%60sr%3D0%60ps%3D1&src_module=search&src_tab_page_id=page_home1724310791925&mallCode=1&pageListType=4&imgRatio=1-1"
    ]
    

    for site in site_to_check:
        
          
            ss=shein(site_to_check[0])
            print(ss)
       

if __name__ == "__main__":
    main()
