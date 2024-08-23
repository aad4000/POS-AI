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

def shein(url, max_attempts=5):
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
            "title": title,
            "price": price
        }
        return result

    finally:
        # Close the driver
        driver.quit()

def main():
    url = "https://ar.shein.com/2023-New-Ultra-Thin-Hard-Shell-Laptop-Case-Compatible-With-Apple-Laptop-Pro-13-A2338-Apple-Laptop-Air-13-A2337-M1-M2-Chip-2022-Apple-Laptop-Air-13-6-A2681-Pro-14-A2442-p-31625154.html?src_identifier=st%3D2%60sc%3Dlaptop%60sr%3D0%60ps%3D1&src_module=search&src_tab_page_id=page_home1724310791925&mallCode=1&pageListType=4&imgRatio=1-1"
    result = shein(url)
    print(result)

if __name__ == "__main__":
    main()
