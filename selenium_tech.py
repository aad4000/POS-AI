from selenium_tech import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
driver=webdriver.Chrome(ChromeDriverManager().install())
for c in range(100,102):
    for i in range(1,40):
        driver.get("https://www.techzone.com.lb/product-category/computer-components/page/"+str(i)+"/"+str(c)+"/")
        elem=driver.find_elements_by_tag_name("img")
        for e in elem:
            print(e.get_attribute("src"))
driver.close()