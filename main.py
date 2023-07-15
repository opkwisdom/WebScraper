from Scraper import WebtoonScraper
import os
import time
import pandas as pd

BASE_PATH = "https://comic.naver.com/webtoon"
days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

scraper = WebtoonScraper(BASE_PATH)
scraper.set_driver_options()

# scrape the links
# scraper.scrape_links()

# links = scraper.get_links()
# for i, link in enumerate(links):
# print(f"{days[i]} / {len(links[i])}: {link}")
# print(len(scraper))

# create a rank database
rank_db = scraper.create_a_rank_database()
print(rank_db)

