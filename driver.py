from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Optional: run Chrome in headless mode
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# Setup WebDriver with webdriver-manager
service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service)

# service = Service('./chromedriver')  # Path to ChromeDriver executable

# Fetch the page
url = "https://gamebroslb.com/products/hyperx-alloy-origins-pbt-hx-red-mechanical-gaming-keyboard"
# url = "https://www.amazon.com/SAMSUNG-Business-Touchscreen-NP944XGK-KG1US-Moonstone/dp/B0CVBKWH12/ref=sr_1_1_sspa?crid=YYESIEPF5999&dib=eyJ2IjoiMSJ9.3K-8z8eTmTn_wSTPLVLLluGoSt3QgXzN5HuHURo2RyRNoTLyVe5aZCwHCBVOpGLLV1IaVRV1nxybXzVsddBrYd_9ck-3t6QZo3s2Ix99tLtF407YrJ77SZ4_XFRCGnPxdWDRotFZ71RdacuRhtN9ANPAjpqo5ye9C_hSLD2hzulz0hOU2y2IJ5KWS4jC-OxqQ_bpviCgDGcJegKM-GGxOeZkqGAEiLd9xiCHUY7wxqM.yqR-YsD676V5xfjATXSy4bSV6aOLaHjwkC24LPug5yo&dib_tag=se&keywords=laptop&qid=1724314624&sprefix=lap%2Caps%2C313&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1"
driver.set_page_load_timeout(60)  # Timeout in seconds

driver.get(url)
html_content = driver.page_source  # Get the HTML content

# You can use BeautifulSoup for further processing if needed
from bs4 import BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')
# productTitle
element = soup.find('span', id = "productTitle")
pretty_html = soup.prettify()

print(element)

# Close the browser
# driver.quit()
