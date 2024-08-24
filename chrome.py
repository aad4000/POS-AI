from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

url = "https://www.amazon.com/SteelSeries-Apex-RGB-Gaming-Keyboard/dp/B07ZGDPT4M/ref=sr_1_1?_encoding=UTF8&content-id=amzn1.sym.12129333-2117-4490-9c17-6d31baf0582a&dib=eyJ2IjoiMSJ9.wDXBdYZ5jTvV8Yb1JBou46dA1SjYNzcFtdtRYFj4dYThMPgXCqv-_N4kHJhaXF1KHZ-jy5a7hQOEOMRZ5EaNqm5eXBT6I5tfYbBvgC4qN-2nTraHdYsXeptePMUXDIcpT7Zi-9t1wKb38VlRhSBUdRVRDRRWdq9i9wWvaMf82o6wb8Cmt-PY840-WLOEx40ytsoxPhfT4xFvDbkPRT7imMt74dGOSDfLjEpEv7rcZnA.T7IUh7VojCd0-lbc0_Eb-vTBlNqBHZmxUhhH0YwXUi8&dib_tag=se&keywords=gaming+keyboard&pd_rd_r=cc9275f6-fe29-44ca-88a9-ed111272801e&pd_rd_w=HaBkI&pd_rd_wg=5kJZf&pf_rd_p=12129333-2117-4490-9c17-6d31baf0582a&pf_rd_r=CKN0A174M8006KB8J8DP&qid=1724142951&sr=8-1"

# Create an Options object
chrome_options = Options()

# Add the desired options
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model, useful for running inside containers
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

# Initialize the Chrome driver with options
  # Use ChromeDriverManager to automatically manage driver
driver = webdriver.Chrome( options=chrome_options)

# Now you can use the driver to navigate to pages, scrape, etc.
driver.get(url)

soup = BeautifulSoup(driver.page_source, "html.parser")

print(soup)