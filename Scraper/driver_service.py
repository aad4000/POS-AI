import re
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import random
from Scraper.static import *

def get_valid_proxy(proxy_file):
    """
    Reads the proxies from the proxy file, shuffles them, 
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


def firefox_driver_setup():
    proxy = get_valid_proxy(PROXY_FILE)
    # proxy_host, proxy_port = proxy.replace("http://", "").split(':')

    options = FirefoxOptions()
    # options.add_argument(f'--proxy-server=http://{proxy_host}:{proxy_port}')

    # options.add_argument("--headless")        
    # options.set_preference("network.proxy.type", 1)  
    # options.set_preference("network.proxy.http", proxy_host)
    # options.set_preference("network.proxy.http_port", int(proxy_port))
    # options.set_preference("network.proxy.ssl", proxy_host)
    # options.set_preference("network.proxy.ssl_port", int(proxy_port))


    print(f"using prpoxy : {proxy}")
    driver_service = FirefoxService()

    driver = webdriver.Firefox(service=driver_service , options= options )
    driver.set_page_load_timeout(TIMEOUT)

    return driver

def chrome_driver_setup():
    # proxy = get_valid_proxy(PROXY_FILE)
    # proxy_host, proxy_port = proxy.replace("http://", "").split(':')

    options = ChromeOptions()
    options.add_argument("--headless")        
    # options.add_argument(f'--proxy-server={proxy}')
    # print(f"using proxy : {proxy}")

    service = ChromeService()

    driver = webdriver.Chrome(service=service , options= options)
    driver.set_page_load_timeout(TIMEOUT)

    return driver

def wait_for_element(driver, by, selector, timeout=TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )

# TODO generalize this
def wait_for_element3(driver, by, selectors, timeout=TIMEOUT):
    # Construct the CSS selector string by joining the individual selectors
    combined_selector = f"{selectors[0]}, {selectors[1]}, {selectors[2]}"
    
    # Wait for the presence of all elements matching the combined selector
    elements = WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located(
            (by, combined_selector)
        )
    )
    
    # Debugging: Print the text of each element
    for i, element in enumerate(elements):
        print(f"Element {i}: {element.text.strip()}")
    
    return elements


def wait_for_element_clickable(driver, by, selector, timeout=TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )
