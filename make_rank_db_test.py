"""
Test for creating a rank database
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd

BASE_PATH = "https://comic.naver.com/webtoon"
day = "?tab=mon"
PATH = BASE_PATH + day

famous_link = []
view_link = []
rate_link = []

options = webdriver.ChromeOptions()
# prevent webdriver from closing immediately
options.add_argument("--headless")
options.add_argument('--window-size=1920,1080')
options.add_experimental_option("detach", True)

# rank by popularity
start = time.time()

driver = webdriver.Chrome(options=options)
driver.get(PATH)
wait = WebDriverWait(driver, timeout=30)

famous = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='content']/div[1]/div/div[2]/button[1]")))
famous.click()

Content = driver.find_element(By.ID, "content")

Link_Info = Content.find_elements(By.CLASS_NAME, "ContentTitle__title_area--x24vt")
for i, link in enumerate(Link_Info):
    famous_link.append((i+1, link.get_attribute("href")))
Famous_sorted = pd.DataFrame(famous_link,
                             columns=["Famous", "Link"])


# rank by view
view = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='content']/div[1]/div/div[2]/button[3]")))
view.click()

Content = driver.find_element(By.ID, "content")

Link_Info = Content.find_elements(By.CLASS_NAME, "ContentTitle__title_area--x24vt")
for i, link in enumerate(Link_Info):
    view_link.append((i+1, link.get_attribute("href")))
View_sorted = pd.DataFrame(view_link,
                           columns=["View", "Link"])


# rank by rate
rate = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='content']/div[1]/div/div[2]/button[4]")))
rate.click()

Content = driver.find_element(By.ID, "content")

Link_Info = Content.find_elements(By.CLASS_NAME, "ContentTitle__title_area--x24vt")
for i, link in enumerate(Link_Info):
    rate_link.append((i+1, link.get_attribute("href")))
Rate_sorted = pd.DataFrame(rate_link,
                             columns=["Rate", "Link"])

driver.close()

end = time.time()

merged = pd.merge(Famous_sorted, View_sorted, on="Link")
merged = pd.merge(merged, Rate_sorted, on="Link")
print(f"Elapsed time: {end - start : .2f}s")
print(merged.shape)
print(Famous_sorted.shape)
print(View_sorted.shape)
print(Rate_sorted.shape)
print(merged)


