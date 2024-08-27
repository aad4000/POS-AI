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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


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
        
        price = soup.find('div', class_='ux-textspans')
        if price:
            price = price.get_text(strip=True)
        else:
            price = "Price not found"
        
        return {"price": price, "description": description}
    else:
        return {"error": f"Request failed with status code {response.status_code}"}
def handle_ebay(response):
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Scrape the product title
        title_element = soup.find('h1', class_='x-item-title__mainTitle')
        if title_element:
            title = title_element.find('span', class_='ux-textspans ux-textspans--BOLD')
            if title:
                description = title.get_text(strip=True)
            else:
                description = "Title not found"
        else:
            description = "Title element not found"
        
        # Scrape the product price
        price_container = soup.find('div', class_='x-price-primary')
        if price_container:
            price_element = price_container.find('span', class_='ux-textspans')
            if price_element:
                price = price_element.get_text(strip=True)
            else:
                price = "Price not found"
        else:
            price = "Price container not found"
        
        return {"price": price, "description": description}
    else:
        return {"error": f"Request failed with status code {response.status_code}"}
def handle_aliExpress(url):
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU (useful for headless mode)
    chrome_options.add_argument("--no-sandbox")  # Required for some environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("window-size=1920,1080")  # Set window size for rendering
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    chrome_options.add_argument("--remote-debugging-port=9222")  # For debugging purposes

    # Automatically install and set up ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the price element to be present and visible
        price_element = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'price--currentPriceText--V8_y_b5'))
        )
        price = price_element.text.strip() if price_element else "Price not found"
        
        # Wait for the title element to be present and visible
        title_element = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'title--wrap--UUHae_g'))
        )
        title = title_element.find_element(By.TAG_NAME, 'h1').text.strip() if title_element else "Title not found"

        # Return the result in the desired format
        return {"price": price, "description": title}

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Close the browserjhneerd
        driver.quit()

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
    elif company_name in known_companies_url:
        handler_function = known_companies_url[company_name]
        return handler_function(url)
        
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
   
def handle_newegg(response):
    if response:
        soup = BeautifulSoup(response.text, "html.parser")

       

        title = soup.find("h1", class_="product-title")
        if title:
            title_text = title.get_text(strip=True)

        
        price_li = soup.find('li', class_='price-current')
        if price_li:
            dollar_part = price_li.find('strong')
            cents_part = price_li.find('sup')

            if dollar_part and cents_part:
                price = f"${dollar_part.get_text(strip=True)}{cents_part.get_text(strip=True)}"
            elif dollar_part: 
                price = f"${dollar_part.get_text(strip=True)}"

        

        
        return  {"price": price, "description": title_text}
    else:
            return json.dumps({"error": "No response"})

           
def handle_ayoub_computer(response):
    if response:
        soup = BeautifulSoup(response.text, "html.parser")

        
        

       
        title = soup.find("h1", class_="productView-title")
        if title:
            title_text = title.get_text(strip=True)

       
        price = soup.find("span", class_="price price--withoutTax price--main")
        if price:
            price_text = price.get_text(strip=True)
        
        

          
        return  {"price": price_text, "description": title_text}
    else:
            return json.dumps({"error": "No response"})
    
def handle_techzone(response):
    """Fetch the title and price from the HTML response."""
    if response:
        soup = BeautifulSoup(response.text, "html.parser")

        
        title = soup.find("h1", class_="product_title entry-title wd-entities-title")
        if title:
           title_text= title.get_text(strip=True)
        

        
        price=soup.find('p', class_='price').find('span', class_='woocommerce-Price-amount')
        if price:
            price_text=price.get_text(strip=True)
        return  {"price": price_text, "description": title_text}
    else:
            return json.dumps({"error": "No response"})
def amazon_captcha_solver(url, max_attempts=5):
    # AWS credentials (For testing purposes only. Avoid hardcoding in production)
    aws_access_key_id = 'AKIA47CRYVZCSF523ZOG'
    aws_secret_access_key = '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'

    # Initialize the Textract client with credentials
    textract_client = boto3.client(
        'textract',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name='us-east-1'
    )

    # Setup Chrome driver in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Navigate to the webpage
    driver.get(url)

    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        try:
            # Wait for the CAPTCHA image to be present
            captcha_image_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='a-row a-text-center']/img"))
            )
            captcha_image_url = captcha_image_element.get_attribute('src')

            # Download the CAPTCHA image
            captcha_image = requests.get(captcha_image_url).content

            # Send the image directly to Textract
            response = textract_client.detect_document_text(
                Document={
                    'Bytes': captcha_image
                }
            )

            # Extract the text detected by Textract
            captcha_text = ''
            for item in response["Blocks"]:
                if item["BlockType"] == "LINE":
                    captcha_text += item["Text"]

            print(f"Solved CAPTCHA (Attempt {attempt}): '{captcha_text}'")

            # Locate the CAPTCHA input field and input the CAPTCHA text
            input_element = driver.find_element(By.ID, "captchacharacters")
            input_element.send_keys(captcha_text)

            # Locate the submit button and click on it
            submit_button = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @class='a-button-text']"))
            )
            submit_button.click()

            # Check if CAPTCHA is still present
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='a-row a-text-center']/img"))
                )
                print(f"CAPTCHA still present after attempt {attempt}. Retrying...")
                continue  # CAPTCHA is still present, so continue the loop to solve it again
            except:
                # CAPTCHA is not present, proceed to scrape the title and price
                break

        except Exception as e:
            print(f"Error during CAPTCHA solving attempt {attempt}: {str(e)}")
            continue

    # Scrape the title after solving CAPTCHA(s)
    try:
        title_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "productTitle"))
        )
        title = title_element.text.strip()

        # Scrape the price
        price_symbol_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='a-price-symbol']"))
        )
        price_whole_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='a-price-whole']"))
        )
        price_fraction_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='a-price-fraction']"))
        )

        # Combine the parts of the price
        price = f"{price_symbol_element.text}{price_whole_element.text}.{price_fraction_element.text}"
        result = {
            "description": title,
            "price": price
        }
        return result

    finally:
        # Close the driver
        driver.quit()

def shein(url, max_attempts=7):
    # AWS credentials (For testing purposes only. Avoid hardcoding in production)
    aws_access_key_id = 'AKIA47CRYVZCSF523ZOG'
    aws_secret_access_key = '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'

    # Initialize the Textract client with credentials
    textract_client = boto3.client(
        'textract',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name='us-east-1'
    )

    # Setup Chrome driver in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Navigate to the webpage
    driver.get(url)

    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        try:
            # Wait for the CAPTCHA image to be present
            captcha_image_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='a-row a-text-center']/img"))
            )
            captcha_image_url = captcha_image_element.get_attribute('src')

            # Download the CAPTCHA image
            captcha_image = requests.get(captcha_image_url).content

            # Send the image directly to Textract
            response = textract_client.detect_document_text(
                Document={
                    'Bytes': captcha_image
                }
            )

            # Extract the text detected by Textract
            captcha_text = ''
            for item in response["Blocks"]:
                if item["BlockType"] == "LINE":
                    captcha_text += item["Text"]

            print(f"Solved CAPTCHA (Attempt {attempt}): '{captcha_text}'")

            # Locate the CAPTCHA input field and input the CAPTCHA text
            input_element = driver.find_element(By.ID, "captchacharacters")
            input_element.send_keys(captcha_text)

            # Locate the submit button and click on it
            submit_button = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @class='a-button-text']"))
            )
            submit_button.click()

            # Check if CAPTCHA is still present
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='a-row a-text-center']/img"))
                )
                print(f"CAPTCHA still present after attempt {attempt}. Retrying...")
                continue  # CAPTCHA is still present, so continue the loop to solve it again
            except:
                # CAPTCHA is not present, proceed to scrape the title and price
                break

        except Exception as e:
            print(f"Error during CAPTCHA solving attempt {attempt}: {str(e)}")
            continue

    # Scrape the title after solving CAPTCHA(s)
    try:
        title_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "product-intro__head-name"))
        )
        title = title_element.text.strip()

        # Scrape the price
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "from.original"))
        )
        price = price_element.text

        # Combine the parts of the price
       
        result = {
            "description": title,
            "price": price
        }
        return result

    finally:
        # Close the driver
        driver.quit()


    
known_companies = {
    "katranji.com": handle_katranji,
    "ayoubcomputers.com": handle_ayoub_computers,
    "www.alibaba.com": handle_alibaba,
    "www.ebay.com": handle_ebay,
    "www.newegg.com": handle_newegg,
    "ayoubcomputers.com": handle_ayoub_computer,
    "techzone.com.lb": handle_techzone
}
known_companies_url = {
    "ar.aliexpress.com": handle_aliExpress ,
    "www.amazon.com": amazon_captcha_solver,
    "us.shein.com": shein
}