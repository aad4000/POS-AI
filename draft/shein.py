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

def shein_product_scraper(url, max_attempts=5):
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
            # Check if CAPTCHA is present
            captcha_present = "captcha" in driver.page_source.lower()
            if captcha_present:
                print(f"CAPTCHA detected (Attempt {attempt}). Manual intervention required.")
                return {"error": "CAPTCHA detected. Manual intervention required."}

            # Extract the title
            title_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-intro__head-name"))
            )
            title = title_element.text.strip()

            # Extract the price
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "from.original"))
            )
            price = price_element.text.strip()

            # Return the result as a dictionary
            result = {
                "title": title,
                "price": price
            }
            return result

        except Exception as e:
            print(f"Error during attempt {attempt}: {str(e)}")
            continue

        finally:
            # Close the driver
            driver.quit()

def main():
    url = "https://ar.shein.com/2023-New-Ultra-Thin-Hard-Shell-Laptop-Case-Compatible-With-Apple-Laptop-Pro-13-A2338-Apple-Laptop-Air-13-A2337-M1-M2-Chip-2022-Apple-Laptop-Air-13-6-A2681-Pro-14-A2442-p-31625154.html"
    result = shein_product_scraper(url)
    print(result)

if __name__ == "__main__":
    main()
