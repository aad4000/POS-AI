import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.opera import OperaDriverManager


# Step 1: Send a GET request to the website
url = "https://example.com"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# response = requests.get(url, headers=headers)
# response.encoding = 'utf-8'

# driver = webdriver.Chrome()  # or any other browser driver
driver = webdriver.Opera()

driver.get(url)


# Step 2: Parse the HTML content of the page with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")

# Step 3: Find all article titles
# Assuming the article titles are inside <h2> tags with a specific class
# titles = soup.find_all("h2", class_="card-title")

# Step 4: Print each title
# for title in titles:
#     print(title.get_text(strip=True))

# Optional: Save the titles to a list or a file
# article_titles = [title.get_text(strip=True) for title in titles]

# Print the list of titles
print(soup)

driver.quit()
