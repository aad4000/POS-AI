import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

url = 'https://www.amazon.com/SteelSeries-Apex-RGB-Gaming-Keyboard/dp/B07ZGDPT4M/'

headers = {
    "User-Agent" : 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36'
}

response = requests.get(url , headers= headers)

print(response.text)