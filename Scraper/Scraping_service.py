import boto3
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests

from botocore.exceptions import ClientError

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

# Step 3: Define the Claude Interaction Function

REGION_NAME = "us-east-1"
MODEL_NAME = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Function to interact with Claude model via AWS Bedrock
def generate_prompt(user_price, scraped_price, score):
    """
    Generate a prompt for the Claude model to compare user-provided price with scraped price,
    focusing solely on price comparison and providing a brief two-line analysis.
    """
    prompt = f"""
    <prompt>
        <task>Price Comparison</task>

        <examples>
            <example>
                <userProvidedPrice>100.00</userProvidedPrice>
                <scrapedPrice>100.00</scrapedPrice>
                <matchScore>100</matchScore>
                <analysis>The prices are exactly the same, resulting in a perfect match score of 100.</analysis>
            </example>
            <example>
                <userProvidedPrice>100.00</userProvidedPrice>
                <scrapedPrice>95.00</scrapedPrice>
                <matchScore>95</matchScore>
                <analysis>The scraped price is slightly lower than the user-provided price, resulting in a high match score of 95.</analysis>
            </example>
            <example>
                <userProvidedPrice>100.00</userProvidedPrice>
                <scrapedPrice>80.00</scrapedPrice>
                <matchScore>80</matchScore>
                <analysis>There is a noticeable difference between the user-provided price and the scraped price, leading to a lower match score of 80.</analysis>
            </example>
        </examples>
        
        <userProvidedPrice>{user_price}</userProvidedPrice>
        <scrapedPrice>{scraped_price}</scrapedPrice>
        <matchScore>{score}</matchScore>
        <detailedAnalysis>
            <description>Provide only a brief two-line analysis focused on the price comparison. Avoid any additional details.</description>
        </detailedAnalysis>
        
        <outputFormat>
            <format type="JSON">
                <![CDATA[
                {{
                    "match_score": {score},
                    "analysis": "Your concise, two-line analysis of the price comparison here."
                }}
                ]]>
            </format>
        </outputFormat>
    </prompt>
    """
    return prompt.strip()
def extract_numerical_price(price_str):
    # Remove any commas and currency symbols from the price string
    cleaned_price_str = re.sub(r'[^\d\.]', '', price_str)
    
    # Find the first sequence of digits, optionally followed by a decimal point and more digits
    match = re.search(r'\d+\.?\d*', cleaned_price_str)
    
    if match:
        return float(match.group())
    else:
        raise ValueError("No numerical part found in the price string.")
def calculate_match_score(user_price, scraped_price):
    # Ensure both prices are now floats
    user_price = float(user_price)
    fscraper_price = float(scraped_price)
    
    print(f"Comparing User price: {user_price} with Scraped price: {fscraper_price}")
    
    # Calculate the absolute difference between the prices
    absolute_difference = abs(user_price - fscraper_price)
    print(f"Absolute difference: {absolute_difference}")
    
    # Calculate the percentage difference relative to the user-provided price
    percentage_difference = (absolute_difference / user_price) * 100
    print(f"Percentage difference: {percentage_difference}")
    
    # Calculate the match score
    score = max(0, 100 - percentage_difference)
    print(f"Calculated score: {score}")
    
    # Return the score as an integer
    return int(score)


def get_completion(prompt):
    try:
        bedrock = boto3.client(service_name="bedrock-runtime", region_name=REGION_NAME)
        body = json.dumps({
            "max_tokens": 100,  # Limit the response length to avoid excess details
            "messages": [{"role": "user", "content": prompt}],
            "anthropic_version": "bedrock-2023-05-31"
        })

        response = bedrock.invoke_model(body=body, modelId=MODEL_NAME)
        response_body = json.loads(response.get("body").read())
        return response_body.get("content")
    except Exception as e:
        print(f"Error communicating with Claude: {e}")
        raise e



def handle_katranji(response):
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        description = soup.find('div', class_='text-xl md:text-2xl xl:text-3xl font-bold mb-4 w-3/4')
        price = soup.find('div', class_='font-bold text-[2.5rem]')
        
        return {
            "price": price.get_text(strip=True) if price else "Price not found",
            "description": description.get_text(strip=True) if description else "Description not found"
        }
    else:
        return {"error": f"Request failed with status code {response.status_code}"}

def handle_alibaba(response):
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h1", title=True)
        price_element = soup.find('div', class_='price')

        if not price_element:
            price_spans = soup.find_all('span')
            price_element = next((span for span in price_spans if "$" in span.text), None)

        return {
            "price": price_element.get_text(strip=True) if price_element else "Price not found",
            "description": title.get_text(strip=True) if title else "Description not found"
        }
    else:
        return {"error": "No response"}

def handle_newegg(response):
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h1", class_="product-title")
        price_li = soup.find('li', class_='price-current')

        if price_li:
            dollar_part = price_li.find('strong')
            cents_part = price_li.find('sup')
            price = f"${dollar_part.get_text(strip=True)}{cents_part.get_text(strip=True)}" if dollar_part and cents_part else f"${dollar_part.get_text(strip=True)}" if dollar_part else "Price not found"
        else:
            price = "Price not found"

        return {
            "price": price,
            "description": title.get_text(strip=True) if title else "Description not found"
        }
    else:
        return {"error": "No response"}

def handle_ayoub_computer(response):
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h1", class_="productView-title")
        price = soup.find("span", class_="price price--withoutTax price--main")

        return {
            "price": price.get_text(strip=True) if price else "Price not found",
            "description": title.get_text(strip=True) if title else "Description not found"
        }
    else:
        return {"error": "No response"}

def handle_techzone(response):
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h1", class_="product_title entry-title wd-entities-title")
        price = soup.find('p', class_='price').find('span', class_='woocommerce-Price-amount')

        return {
            "price": price.get_text(strip=True) if price else "Price not found",
            "description": title.get_text(strip=True) if title else "Description not found"
        }
    else:
        return {"error": "No response"}

# Step 5: Map Companies to Handlers
def get_secret(secret_name):
    # Initialize a session using Amazon Secrets Manager
    client = boto3.client('secretsmanager', region_name='us-east-1')

    try:
        # Retrieve the secret
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']

        # Print the secret string to inspect it
        print("Secret String:", repr(secret))

        # Load the secret string as JSON
        secret_json = json.loads(secret)
        return secret_json
    except ClientError as e:
        raise e
    except json.JSONDecodeError as json_err:
        print(f"Error decoding JSON: {json_err}")
        raise

def handle_amazon(url, max_attempts=5):
    # AWS credentials (For testing purposes only. Avoid hardcoding in production)
    secret = get_secret('AcessKey')

    # Initialize the Textract client with credentials
    textract_client = boto3.client(
        'textract',
        aws_access_key_id=secret['aws_access_key_id'],
        aws_secret_access_key=secret['aws_secret_access_key'],
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
            "title": title,
            "price": price
        }
        return result

    finally:
        # Close the driver
        driver.quit()

known_companies = {
    "katranji.com": handle_katranji,
    "www.alibaba.com": handle_alibaba,
    "ayoubcomputers.com": handle_ayoub_computer,
    "newegg.com": handle_newegg,
    "techzone.com.lb": handle_techzone
}
known_companiess = {
    "amazon.com": handle_amazon
}

def fetch_product(url):
    company_name = extract_company_name(urlparse(url).netloc)
    
    # Debugging: Check which company is being matched
    print(f"Checking company name: {company_name}")
    
    if company_name in known_companies:
        print(f"Company found in known_companies: {company_name}")
        response = get_response(url)
        if isinstance(response, dict) and "error" in response:
            return response 
        handler_function = known_companies[company_name]
        return handler_function(response)
    
    if company_name in known_companiess:
        print(f"Company found in known_companiess: {company_name}")
        handler_function = known_companiess[company_name]
        return handler_function(url)
    
    else:
        print(f"Company not supported: {company_name}")
        return {"error": f"Company not supported: {company_name}"}

def extract_company_name(netloc):
    """Extracts the company name (domain) from the netloc."""
    company_name = netloc.lower().replace("www.", "")
    print(f"Extracted company name: {company_name}")
    return company_name


def main():
    url = "https://www.amazon.com/SAMSUNG-Business-Touchscreen-NP944XGK-KG1US-Moonstone/dp/B0CVBKWH12"
    result = fetch_product(url)
    print(result)
if __name__ == "__main__":
    main()