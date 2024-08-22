from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Navigate to the webpage
url = "https://ar.shein.com/Auusda-Laptop-Computer-T152A-With-15-6-FHD-IPS-LCD-Screen-Intel-Up-To-2-3-4-GHz-Backlight-Keyboard-Fingerprint-Reader-Mini-HD-USB-A-X2-Windows-11-Pro-16-32GB-DDR4-RAM-512GB-1TB-M-2-PCIe-NVMe-SSD-Pink-p-29510459.html?src_identifier=st%3D2%60sc%3Dlaptop%60sr%3D0%60ps%3D1&src_module=search&src_tab_page_id=page_home1724310791925&mallCode=1&pageListType=4&imgRatio=1-1"
driver.get(url)

# Wait until the title element is present
try:
    # Extract the title
    title_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product-intro__head-name"))
    )
    title = title_element.text
    print("Title:", title)

    # Extract the price
    price_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "from.original"))
    )
    price = price_element.text
    print("Price:", price)

finally:
    # Close the driver
    driver.close()
