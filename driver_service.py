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

def get_random_proxy(proxy_file):
    with open(proxy_file, "r") as f:
        proxies = [line.strip() for line in f if line.strip()]
    return random.choice(proxies) if proxies else None


def firefox_driver_setup():
    proxy = get_random_proxy("./valid_proxies.txt")
    proxy_host, proxy_port = proxy.replace("http://", "").split(':')

    options = FirefoxOptions()
    options.add_argument(f'--proxy-server=http://{proxy_host}:{proxy_port}')

    # options.add_argument("--headless")        
    # options.set_preference("network.proxy.type", 1)  
    # options.set_preference("network.proxy.http", proxy_host)
    # options.set_preference("network.proxy.http_port", int(proxy_port))
    # options.set_preference("network.proxy.ssl", proxy_host)
    # options.set_preference("network.proxy.ssl_port", int(proxy_port))


    print(f"using prpoxy : {proxy}")
    driver_service = FirefoxService()

    driver = webdriver.Firefox(service=driver_service , options= options )
    driver.set_page_load_timeout(120)

    return driver

def chrome_driver_setup():
    proxy = get_random_proxy("./valid_proxies.txt")
    proxy_host, proxy_port = proxy.replace("http://", "").split(':')

    options = ChromeOptions()
    # options.add_argument("--headless")        
    # options.add_argument(f'--proxy-server={proxy}')
    # print(f"using proxy : {proxy}")

    service = ChromeService()

    driver = webdriver.Chrome(service=service , options= options)
    driver.set_page_load_timeout(120)

    return driver

def wait_for_element(driver, by, selector, timeout=120):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )

def wait_for_element_clickable(driver, by, selector, timeout=120):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )
