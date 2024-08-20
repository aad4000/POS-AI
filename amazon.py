import requests
from bs4 import BeautifulSoup

# Step 1: Send a GET request to the website
url = "https://www.amazon.com/SteelSeries-Apex-RGB-Gaming-Keyboard/dp/B07ZGDPT4M/ref=sr_1_1?_encoding=UTF8&content-id=amzn1.sym.12129333-2117-4490-9c17-6d31baf0582a&dib=eyJ2IjoiMSJ9.wDXBdYZ5jTvV8Yb1JBou46dA1SjYNzcFtdtRYFj4dYThMPgXCqv-_N4kHJhaXF1KHZ-jy5a7hQOEOMRZ5EaNqm5eXBT6I5tfYbBvgC4qN-2nTraHdYsXeptePMUXDIcpT7Zi-9t1wKb38VlRhSBUdRVRDRRWdq9i9wWvaMf82o6wb8Cmt-PY840-WLOEx40ytsoxPhfT4xFvDbkPRT7imMt74dGOSDfLjEpEv7rcZnA.T7IUh7VojCd0-lbc0_Eb-vTBlNqBHZmxUhhH0YwXUi8&dib_tag=se&keywords=gaming+keyboard&pd_rd_r=cc9275f6-fe29-44ca-88a9-ed111272801e&pd_rd_w=HaBkI&pd_rd_wg=5kJZf&pf_rd_p=12129333-2117-4490-9c17-6d31baf0582a&pf_rd_r=CKN0A174M8006KB8J8DP&qid=1724142951&sr=8-1"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

# Step 2: Parse the HTML content of the page with BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

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
