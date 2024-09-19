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

'''
Adaptable dynamic function based on website configuration 
selenium based
'''

CONFIG = {
    "gamebroslb": {
        "description_selector": "div.product__title h1",
        "price_selector":"span.price-item.price-item--regular",
    },
    "460estore": {
        "description_selector": "h1.namne_details",
        "price_selector": "span[itemprop='price'][content='5']"
    },
    "amazon" : {
        "description_selector": "#productTitle",
        "price_selector": "div.a-section.a-spacing-micro",
        "captcha" : "image_text"
    }

}

def get_domain(url):
    '''
        takes : https://gamebroslb.com/products/stuff/whatever
        returns : gamebroslb
    '''

    match = re.search(r"https?://(www\.)?([^/]+)", url)
    
    if match:
        origin = match.group(2).split('.')[0]
        return origin
    else:
        return None

def dynamic_scraper(url):
    
    domain = get_domain(url) # > assuming url already validated
    config = CONFIG[domain]

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

    description = wait_for_element(driver , By.CSS_SELECTOR , description_selector).text
    price = wait_for_element(driver , By.CSS_SELECTOR , price_selector).text

    #> return values
    print(f"{description}  :  price is {price}")

    input()
    driver.quit()





url = "https://gamebroslb.com/products/hyperx-alloy-origins-pbt-hx-red-mechanical-gaming-keyboard"

url9 = "https://460estore.com/gaming-keyboard-mouse/6374-hoco-gaming-luminous-wired-mouse.html?gad_source=1&gclid=CjwKCAjwoJa2BhBPEiwA0l0ImET5zvEL495rZ4tYF4LyJU188oTC86MBqijx5k4HrzLHYVsAwcZ32xoCIisQAvD_BwE"

url = "https://www.amazon.com/Lenovo-Legion-K310-Gaming-Keyboard/dp/B0CV915WG6/ref=sr_1_1_sspa?c=ts&dib=eyJ2IjoiMSJ9.S6hJiufPu9YsnPIPJRMmSoKh-v8TubqPz6SE-AAhr6R-K17hxIwA4fOpSrzBs7NgiS6_Sa4qQfyWaqT3tSx7eRz8HGe0UEtrVg-b_kS1UzohHenfAHBdc5e6uQGWxXdUfPWmn-LceTcKydiQXtZH3x8zAyklw7d3yzv9438hjDycgrf2f6TBwaUFeJYkiJ_QUa_YCimLY6D29fZpT2jOmHeaBjPq1RFAR-ApnKYJu4JvW81uNGVa1oye-XuTo7ohsdmbAG0XoGAKwT7-xr33cWYZC6rZGtFeNm5pwFDYdvE.NMdfUKM4o5xaNeWGVxWiiEGCx55IuYR5ZtFYPP9efNA&dib_tag=se&keywords=Computer+Keyboards&qid=1724329568&s=pc&sr=1-1-spons&ts_id=12879431&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1"

dynamic_scraper(url)

