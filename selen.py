from selenium import webdriver
import time
from bs4 import BeautifulSoup


driver = webdriver.Chrome()

driver.get("https://www.facebook.com/")

fb_id = driver.find_element_by_xpath('//*[@id="email"]')

fb_pass = driver.find_element_by_xpath('//*[@id="pass"]')





keys_id = input("facebook id gir:")
keys_pass = input("sifre gir : ")
fb_id.send_keys(f"{keys_id}")
fb_pass.send_keys(f"{keys_pass}")

time.sleep(1)

soup_object = BeautifulSoup(driver.page_source,"html.parser")
d1 = soup_object.find("div", attrs={"class": "_6ltg"})
driver.get(d1)



