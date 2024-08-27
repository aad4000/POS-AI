from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Setup Chrome options to run in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Setup Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open a web page
url = "https://ar.shein.com/2023-New-Ultra-Thin-Hard-Shell-Laptop-Case-Compatible-With-Apple-Laptop-Pro-13-A2338-Apple-Laptop-Air-13-A2337-M1-M2-Chip-2022-Apple-Laptop-Air-13-6-A2681-Pro-14-A2442-p-31625154.html"
driver.get(url)

# Get the page source
page_source = driver.page_source

# Save the page source to a file
with open("page_source.html", "w", encoding="utf-8") as file:
    file.write(page_source)

# Close the WebDriver
driver.quit()

# Re-open the saved HTML file and parse it with BeautifulSoup
with open("page_source.html", "r", encoding="utf-8") as file:
    saved_page_source = file.read()

soup = BeautifulSoup(saved_page_source, 'html.parser')

# Find the product title using the correct HTML tag and class
product_title = soup.find('span', class_='product-intro__head-name')  # Adjust class name based on actual HTML

# Find the product price using the correct HTML tag and class
product_price = soup.find('span', class_='product-intro__price')  # Adjust class name based on actual HTML

# Check if the product title and price were found and print them
if product_title:
    print(f"Product Title: {product_title.get_text(strip=True)}")
else:
    print("Product title not found.")

if product_price:
    print(f"Product Price: {product_price.get_text(strip=True)}")
else:
    print("Product price not found.")
