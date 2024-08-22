import boto3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests

# Initialize the Textract client
textract_client = boto3.client('textract')

# Setup Chrome driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Navigate to the webpage
url = "https://www.amazon.com/SAMSUNG-Business-Touchscreen-NP944XGK-KG1US-Moonstone/dp/B0CVBKWH12"
driver.get(url)

try:
    # Check if CAPTCHA is present by looking for the CAPTCHA image
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

    print(f"Solved CAPTCHA: '{captcha_text}'")

    # Locate the CAPTCHA input field and input the CAPTCHA text
    input_element = driver.find_element(By.ID, "captchacharacters")
    input_element.send_keys(captcha_text)

    # Submit the CAPTCHA form
    submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
    submit_button.click()

    # Wait and scrape the title
    title_element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "productTitle"))
    )
    title = title_element.text.strip()
    print("Title:", title)

    # Scrape the price
    price_element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//span[@class='a-price']//span[@aria-hidden='true']"))
    )
    price = price_element.text.strip()
    print("Price:", price)

finally:
    # Close the driver
    driver.quit()
