from Scraper import WebtoonScraper
import os
import time
import pandas as pd

BASE_PATH = "https://comic.naver.com/webtoon"
days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

scraper = WebtoonScraper(BASE_PATH)
scraper.set_driver_options()
scraper.scrape_links()

links = scraper.get_links()
for i, link in enumerate(links):
    print(f"{days[i]} / {len(links[i])}: {link}")
