import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import boto3
from botocore.exceptions import NoCredentialsError
import os


# TODO: modify script to use selenium item scans only 
# TODO: handle if captcha folder auto creation if !exists
# TODO: handle errors (4 currently known) :
# 1- connection timing out error 
# 2- multipe captcha
# 3- no captcha
# 4- textract mistaking   
# TODO: refactor code for modularity


url = "https://www.amazon.com/Lenovo-Legion-K310-Gaming-Keyboard/dp/B0CV915WG6/ref=sr_1_1_sspa?c=ts&dib=eyJ2IjoiMSJ9.S6hJiufPu9YsnPIPJRMmSoKh-v8TubqPz6SE-AAhr6R-K17hxIwA4fOpSrzBs7NgiS6_Sa4qQfyWaqT3tSx7eRz8HGe0UEtrVg-b_kS1UzohHenfAHBdc5e6uQGWxXdUfPWmn-LceTcKydiQXtZH3x8zAyklw7d3yzv9438hjDycgrf2f6TBwaUFeJYkiJ_QUa_YCimLY6D29fZpT2jOmHeaBjPq1RFAR-ApnKYJu4JvW81uNGVa1oye-XuTo7ohsdmbAG0XoGAKwT7-xr33cWYZC6rZGtFeNm5pwFDYdvE.NMdfUKM4o5xaNeWGVxWiiEGCx55IuYR5ZtFYPP9efNA&dib_tag=se&keywords=Computer+Keyboards&qid=1724329568&s=pc&sr=1-1-spons&ts_id=12879431&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1"

 
# > create driver , get url
driver = webdriver.Firefox()
driver.get(url)

# > search driver url
soup = BeautifulSoup(driver.page_source, "html.parser")

# > get captcha image
img_element = soup.find('img', {'src': re.compile(r'captcha/.+/Captcha_.+\.jpg')})

if(not img_element) : raise Exception("Couldn't Find captcha image")

img_url = img_element['src']
img_bin = requests.get(img_url)

with open('captcha/captcha_image.jpg', 'wb') as file:
    file.write(img_bin.content)

# > send to textract
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')

textract_client = boto3.client(
    'textract',
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

image_path = 'captcha/captcha_image.jpg'

with open(image_path, 'rb') as image_file:
    image_bytes = image_file.read()

try:
    response = textract_client.detect_document_text(
        Document={'Bytes': image_bytes}
    )
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            captchaChars = item['Text']

except Exception as e:
    print(f"Error calling Textract: {e}")

# > input captcha 
input_element = driver.find_element(By.ID, "captchacharacters")
input_element.send_keys(captchaChars)

# > press submit
button = driver.find_element(By.CLASS_NAME, 'a-button-text')
button.click()

# > extract info
description = driver.find_element(By.ID,"productTitle").text
price = driver.find_element(By.CLASS_NAME,"a-price-whole").text
fractionPrice = driver.find_element(By.CLASS_NAME,"a-price-fraction").text

print(description , price , fractionPrice , sep="\n")

# ? block for testing
input()

driver.quit()
