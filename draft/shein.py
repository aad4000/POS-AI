import boto3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests

def detect_text_from_image(image_bytes):
    rekognition_client = boto3.client('rekognition', region_name='us-east-1')

    response = rekognition_client.detect_text(
        Image={
            'Bytes': image_bytes
        }
    )

    detected_text = ""
    for text in response['TextDetections']:
        if text['Type'] == 'LINE':
            detected_text += text['DetectedText']

    return detected_text

def solve_captcha_with_rekognition(captcha_image_url):
    response = requests.get(captcha_image_url)
    captcha_text = detect_text_from_image(response.content)
    return captcha_text

def shein(url):
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the webpage
        driver.get(url)

        # Detect CAPTCHA image
        captcha_image_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//img[@class='a-row a-text-center']"))  # Replace with the actual XPath of the CAPTCHA image
        )
        captcha_image_url = captcha_image_element.get_attribute('src')

        # Solve CAPTCHA using AWS Rekognition
        captcha_text = solve_captcha_with_rekognition(captcha_image_url)
        print(f"Solved CAPTCHA: {captcha_text}")

        # Enter the CAPTCHA solution
        input_element = driver.find_element(By.ID, "captchacharacters")
        input_element.send_keys(captcha_text)

        # Submit the CAPTCHA form
        submit_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        submit_button.click()

        # Continue scraping after CAPTCHA is solved

        # Extract the title
        title_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-intro__head-name"))
        )
        title = title_element.text

        # Extract the price
        price_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "from.original"))
        )
        price = price_element.text

        # Return the result as a list
        return [title, price]

    finally:
        # Close the driver
        driver.quit()

def main():
    url = "https://ar.shein.com/2023-New-Ultra-Thin-Hard-Shell-Laptop-Case-Compatible-With-Apple-Laptop-Pro-13-A2338-Apple-Laptop-Air-13-A2337-M1-M2-Chip-2022-Apple-Laptop-Air-13-6-A2681-Pro-14-A2442-p-31625154.html"
    result = shein(url)
    print(result)

if __name__ == "__main__":
    main()
