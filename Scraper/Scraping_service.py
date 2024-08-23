# services.py
import re
import requests
import random
from bs4 import BeautifulSoup
import json
from flask import jsonify
import boto3
from urllib.parse import urlparse
from botocore.exceptions import ClientError

def get_valid_proxy(proxy_file):
    """
    Reads the proxies from the proxy file (plain text format), shuffles them, 
    and returns a list of valid HTTP/HTTPS proxies.
    """
    try:
        with open(proxy_file, 'r') as f:
            proxies = f.read().splitlines()  

        if not proxies:
            return {"error": "Proxy file is empty or contains no valid proxies"}
        
        random.shuffle(proxies)
        return {"proxies": proxies}

    except FileNotFoundError:
        return {"error": f"Proxy file '{proxy_file}' not found."}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def handle_katranji(response): 
    if response.status_code == 200:
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
        
        return {"price": price, "description": description}
    else:
        return {"error": f"Request failed with status code {response.status_code}"}

def get_response(url):
    proxy_file = 'lib/active_proxies.txt'
    max_retries = 5
    proxies_json = get_valid_proxy(proxy_file)
    if "error" in proxies_json:
        return {"error": proxies_json['error']}

    proxies = proxies_json['proxies']
    retry_count = 0

    for proxy in proxies:
        if retry_count >= max_retries:
            return {"error": f"Reached maximum retry limit of {max_retries}."}
        
        if proxy.startswith("http://") or proxy.startswith("https://"):
            scheme, proxy_address = proxy.split('://')
            proxy_dict = {scheme: f"{scheme}://{proxy_address}"}
            
            try:
                response = requests.get(url, proxies=proxy_dict, timeout=10)
                response.raise_for_status()  
                return response  
            except requests.exceptions.RequestException as e:
                retry_count += 1
                last_error = str(e)
    
    return {"error": f"All proxies failed after {max_retries} retries.", "last_error": last_error}


def handle_ayoub_computers(response):
    '''
    Function to scrape the price and description of a product from Ayoub Computers website.
    '''
    # This function needs to be implemented according to the specific structure of the Ayoub Computers website.
    pass

def fetch_product(url):
    company_name = extract_company_name(urlparse(url).netloc)
    if company_name in known_companies:
        response = get_response(url)
        if isinstance(response, dict) and "error" in response:
            return response 
        handler_function = known_companies[company_name]
        return handler_function(response)
    else:
        return {"error": "Company not supported"}
    
def extract_company_name(netloc):
    """Extracts the company name (domain) from the netloc."""
    return netloc.split(':')[0].lower()  

def handle_alibaba(response):
        if response:
            soup = BeautifulSoup(response.text, "html.parser")
        
            # Initialize default values
            title_text = ""
            price_text = ""

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
          

            # Return the result as a JSON object
            return  {"price": price_text, "description": title_text}
        else:
            return json.dumps({"error": "No response"})
   
    
    
    
    
known_companies = {
    "katranji.com": handle_katranji,
    "ayoubcomputers.com": handle_ayoub_computers,
    "www.alibaba.com": handle_alibaba
}