from Scraper import WebtoonScraper
import os
import time
import pandas as pd
import numpy as np

BASE_PATH = "https://comic.naver.com/webtoon"
days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

scraper = WebtoonScraper(BASE_PATH)
scraper.set_driver_options()

# scrape the links
# scraper.scrape_links()

# make webtoon db
webtoon_db = scraper.create_database()
webtoon_db.to_csv('webtoon_db.csv', index=False)

df = pd.read_csv('WebScraper/webtoon_db.csv')
print(df)
print(df.info())

# links = scraper.get_links()
# with open("links.txt", "w") as f:
#     for link in links:
#         f.write(link + "\n")
# print(links)
# print(len(links))


