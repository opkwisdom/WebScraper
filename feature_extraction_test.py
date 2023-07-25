from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd
import numpy as np
import re

PATH = "https://comic.naver.com/webtoon/list?titleId=648419"


options = webdriver.ChromeOptions()
# prevent webdriver from closing immediately
options.add_argument('--window-size=1920,1080')
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
driver.get(PATH)
# Wait up to 10 seconds for the webpage to load
driver.implicitly_wait(10)

features = []

# feature extraction
# Title
title = driver.find_elements(By.CLASS_NAME, "EpisodeListInfo__title--mYLjC")[0].text

# Writer, Painter
# "ContentMetaInfo__category--WwrCp" (카테고리) 기준으로 "글", "그림", "글/그림" 존재
# 우선 if문으로 처리
author_info = driver.find_elements(By.CLASS_NAME, "ContentMetaInfo__category--WwrCp")[0].text.split("\n")[0]
if author_info == "글/그림":
    writer = painter = driver.find_elements(By.CLASS_NAME, "ContentMetaInfo__link--xTtO6")[0].text
else:
    writer = driver.find_elements(By.CLASS_NAME, "ContentMetaInfo__link--xTtO6")[0].text
    painter = driver.find_elements(By.CLASS_NAME, "ContentMetaInfo__link--xTtO6")[1].text

# Serial Date, Serial Rate
serial_info = driver.find_elements(By.CLASS_NAME, "ContentMetaInfo__info_item--utGrf")[0].text
serial_info = serial_info.split('∙')
serial_info = [item.replace('\n', '') for item in serial_info]

serial_date = serial_info[:-1]
serial_rate = serial_info[-1]

# Tags, Genre
tags_info = driver.find_elements(By.CLASS_NAME, "TagGroup__tag--xu0OH")
tags = [i.text for i in tags_info]
genre = tags[0]

# Likes
likes = driver.find_elements(By.CLASS_NAME, "EpisodeListUser__count--fNEWK")[0].text

# Summary
summary = driver.find_elements(By.CLASS_NAME, "EpisodeListInfo__summary--Jd1WG")[0].text

# Total Publishes
total_publishes = driver.find_elements(By.CLASS_NAME, "EpisodeListView__count--fTMc5")[0].text
total_publishes = total_publishes.split()[1]

features.append([PATH, title, writer, painter, serial_date, serial_rate, genre,
                tags, likes, total_publishes, summary])
print(features)

webtoon_info = pd.DataFrame(features,
                            columns=["Link", "Title", "Writer", "Painter", "Serial_Date", "Serial_Rate",
                                     "Genre", "Tags", "Likes", "Total_Publishes", "Description"])
webtoon_info.to_csv('test.csv')
driver.quit()

