from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager



# > driver options
driver_options = Options()

# driver_options.add_argument("--headless")  # Optional
# driver_options.add_argument("--no-sandbox")
# driver_options.add_argument("--disable-dev-shm-usage")

# > driver service
# service = Service(GeckoDriverManager().install())
# ! installing driver breaks headless option
service = Service()

# > driver
driver = webdriver.Firefox(service=service , options= driver_options)
driver.set_page_load_timeout(60)  # Timeout 


# > get page
url = "https://gamebroslb.com/products/hyperx-alloy-origins-pbt-hx-red-mechanical-gaming-keyboard"

driver.get(url)
html_content = driver.page_source  

# > get element
element = driver.find_element(By.CSS_SELECTOR, 'div.product__title h1')
print(element.text)

# > close browser
driver.quit()
