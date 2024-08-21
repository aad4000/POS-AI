# services.py

import requests
import random
from bs4 import BeautifulSoup
import json

def check_proxy(proxy):
    """
    Function to check if a given proxy is active.
    """
    url = "http://httpbin.org/ip"
    try:
        response = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=5)
        if response.status_code == 200:
            return {"proxy": proxy, "status": "working"}
    except requests.exceptions.RequestException as e:
        return {"proxy": proxy, "status": "failed", "error": str(e)}

def filter_active_proxies(input_file, output_file):
    """
    Reads a list of proxies from an input file, checks which ones are active,
    and writes the active proxies to an output file in JSON format.
    """
    with open(input_file, 'r') as file:
        proxies = file.readlines()
    
    active_proxies = []
    
    for proxy in proxies:
        proxy = proxy.strip()
        if proxy.startswith('http://') or proxy.startswith('socks4://'):
            result = check_proxy(proxy)
            if result['status'] == "working":
                active_proxies.append(proxy)
    
    with open(output_file, 'w') as file:
        json.dump(active_proxies, file)
    
    return {"active_proxies": active_proxies, "output_file": output_file}

def get_valid_proxy(proxy_file):
    """
    Reads the proxies from the proxy file (plain text format), shuffles them, 
    and returns a list of valid HTTP/HTTPS proxies.
    """
    try:
        with open(proxy_file, 'r') as f:
            proxies = f.read().splitlines()  # Read lines and remove any newline characters

        if not proxies:
            return {"error": "Proxy file is empty or contains no valid proxies"}
        
        random.shuffle(proxies)
        return {"proxies": proxies}

    except FileNotFoundError:
        return {"error": f"Proxy file '{proxy_file}' not found."}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def scrape_price_and_description(url, proxy):
    """
    Fetches the HTML content from the URL using the given proxy, scrapes price and description.
    Returns the result as a JSON object.
    """
    scheme, proxy_address = proxy.split('://')
    proxy_dict = {scheme: f"{scheme}://{proxy_address}"}

    try:
        response = requests.get(url, proxies=proxy_dict, timeout=10)
        if response.status_code == 200 :
            soup = BeautifulSoup(response.content, 'html.parser')
            
            description = soup.find('div', class_='text-xl md:text-2xl xl:text-3xl font-bold mb-4 w-3/4')
            if description:
                description = description.get_text(strip=True)
            else:
                description = "Description not found"
            
            price = soup.find('div', class_='font-bold text-[2.5rem]')
            if price:
                price = price.get_text(strip=True)
            else:
                price = "Price not found"
            
            return {"price": price, "description": description, "proxy": proxy}
        else:
            return {"error": f"Request failed with status code {response.status_code}", "proxy": proxy}
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "proxy": proxy}
