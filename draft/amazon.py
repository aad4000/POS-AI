import boto3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
from botocore.exceptions import ClientError

def get_secret(secret_name):
    # Initialize a session using Amazon Secrets Manager
    client = boto3.client('secretsmanager', region_name='us-east-1')

    try:
        # Retrieve the secret
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except ClientError as e:
        raise e

def amazon_captcha_solver(url, max_attempts=5):
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

def main():
    url = "https://www.amazon.com/SAMSUNG-Business-Touchscreen-NP944XGK-KG1US-Moonstone/dp/B0CVBKWH12"
    result = amazon_captcha_solver(url)
    print(result)

if __name__ == "__main__":
    main()
