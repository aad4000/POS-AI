import re
from urllib.parse import urlparse
import requests
import random
from captcha_service import *
from driver_service import *
import requests
from bs4 import BeautifulSoup
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
from captcha_service import *
from driver_service import *
from static import *



def extract_company_name(url):
    """Extracts the company name (domain) from the netloc."""
    netloc = urlparse(url).netloc
    company_name = netloc.lower().replace("www.", "").replace(".com", "")
    print(f"Extracted company name: {company_name}")
    return company_name


def get_response(url):
    max_retries = GET_RESPONSE_MAX_ATTEMPS
    proxies_json = get_valid_proxy(PROXY_FILE)

    if "error" in proxies_json:
        return {"error": proxies_json['error']}
    
    proxies = proxies_json['proxies']
    retry_count = 0

    for proxy in proxies:
        if retry_count >= max_retries:
            return {"error": f"Reached maximum retry limit of {max_retries}."}
        
        scheme, proxy_address = proxy.split('://')
        proxy_dict = {scheme: f"{scheme}://{proxy_address}"}
        
        try:
            response = requests.get(url, proxies=proxy_dict, timeout=PROXY_TIMEOUT)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            retry_count += 1
            last_error = str(e)
    
    return {"error": f"All proxies failed after {max_retries} retries.", "last_error": last_error}


def dynamic_bs4(url):
    
    domain = extract_company_name(url) # > assuming url already validated
    config = CONFIG_BS4[domain]

    response = get_response(url)
    if(not response): return {"error": "No response"}

    soup = BeautifulSoup(response.content, "html.parser")

    # TODO 
    # optional Best practice config
    #recheck amazon price selector
    

    # > mandatory config
    description_selector = config["description_selector"]
    price_selector = config["price_selector"]

    description_element = soup.select_one(description_selector)
    price_element = soup.select_one(price_selector)

    #> return values
    return {
            "price": price_element.get_text(strip=True) if price_element else "Price not found",
            "description": description_element.get_text(strip=True) if description_element else "Description not found"
        }


def dynamic_selenium(url):
    try :
        domain = extract_company_name(url) # > assuming url already validated
        config = CONFIG_SELENIUM[domain]

        driver = firefox_driver_setup()
        driver.get(url)

        if("captcha" in config):
            captchaType = config["captcha"]
            handle_captcha(captchaType , driver)

        # TODO 
        # optional Best practice config
        # proxy usage
        #recheck amazon price selector
        

        # > mandatory config
        description_selector = config["description_selector"]
        price_selector = config["price_selector"]

        description_element = wait_for_element(driver , By.CSS_SELECTOR , description_selector)
        price_element = wait_for_element(driver , By.CSS_SELECTOR , price_selector)

        #> return values

        return {
                "price": price_element.text if price_element else "Price not found",
                "description": description_element.text if description_element else "Description not found"
            }
    
    finally:
        driver.quit()



url = "https://460estore.com/gaming-keyboard-mouse/6374-hoco-gaming-luminous-wired-mouse.html?gad_source=1&gclid=CjwKCAjwoJa2BhBPEiwA0l0ImET5zvEL495rZ4tYF4LyJU188oTC86MBqijx5k4HrzLHYVsAwcZ32xoCIisQAvD_BwE"
dynamic_bs4(url)