from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pytesseract
from PIL import Image, ImageOps
import requests
import time

# Load proxies from file
with open("valid_proxy.txt") as f:
    proxies = f.read().splitlines()

# Function to initialize the driver with a given proxy
def init_driver(proxy):
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server={proxy}')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# Function to preprocess the CAPTCHA image
def preprocess_captcha(image_path):
    captcha_image = Image.open(image_path)
    captcha_image = captcha_image.convert("L")  # Convert to grayscale
    captcha_image = ImageOps.invert(captcha_image)  # Invert image colors
    captcha_image = captcha_image.point(lambda p: p > 128 and 255)  # Apply binary thresholding
    captcha_image.save("preprocessed_captcha.png")  # Save for debugging
    return captcha_image

# Function to solve CAPTCHA using Tesseract OCR
def solve_captcha_with_tesseract(captcha_image_path):
    preprocessed_image = preprocess_captcha(captcha_image_path)
    captcha_text = pytesseract.image_to_string(preprocessed_image).strip()
    return captcha_text

# Main function
def main():
    for proxy in proxies:
        try:
            print(f"Trying proxy: {proxy}")
            driver = init_driver(proxy)

            # Navigate to the Amazon product page
            url = "https://www.amazon.com/SAMSUNG-Business-Touchscreen-NP944XGK-KG1US-Moonstone/dp/B0CVBKWH12"
            driver.get(url)

            # Wait until the title element is present using XPath
            title_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//span[@id='productTitle']"))
            )
            title = title_element.text
            print("Title:", title)

            # Check if CAPTCHA is present by looking for the CAPTCHA image
            captcha_image_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//img[contains(@src, 'captcha')]"))
            )
            captcha_image_url = captcha_image_element.get_attribute('src')

            # Download the CAPTCHA image
            captcha_image = requests.get(captcha_image_url).content
            captcha_image_path = "captcha_image.png"
            with open(captcha_image_path, "wb") as f:
                f.write(captcha_image)

            # Solve the CAPTCHA using Tesseract OCR
            captcha_text = solve_captcha_with_tesseract(captcha_image_path)
            print(f"Solved CAPTCHA: '{captcha_text}'")

            # Locate the CAPTCHA input field and input the CAPTCHA text
            input_element = driver.find_element(By.ID, "captchacharacters")
            input_element.send_keys(captcha_text)

            # Optionally, submit the form or click the submit button
            # submit_button = driver.find_element(By.ID, "submit-button-id")  # Replace with actual button ID
            # submit_button.click()

            # Pause to see results before closing
            time.sleep(5)
            
            # If successful, break out of the loop
            break

        except Exception as e:
            print(f"An error occurred with proxy {proxy}: {e}")
        finally:
            # Close the driver
            driver.quit()

    print("Finished proxy rotation.")

# Run the main function
if __name__ == "__main__":
    main()
