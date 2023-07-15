"""
WebtoonScraper Class

method
1. scrap_links(self, day) : scrap the links for the day of the week
                            parameter day must be in one of the following formats
                            ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
2. get_links(self) : get the scraped links of the class instance
3. make_raw_database(self) : create a database based on the links, and return the pandas csv object.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd


class ScrapeCheck(Exception):
    pass


class WebtoonScraper:
    def __init__(self, base_path):
        self.base_path = base_path
        self.links = []
        self.is_scraped = False
        self.raw_database = pd.DataFrame(columns=["Title", "Author", "Day",
                                                  "Likes", "Episodes", "description",
                                                  "Rank"])
        self.options = webdriver.ChromeOptions()

    # set the WebDriver options
    def set_driver_options(self):
        self.options.add_argument("headless")
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        # prevent webdriver from closing immediately
        self.options.add_experimental_option("detach", True)

    # scrape webtoon links according to given day
    def scrape_links(self):
        if self.is_scraped:
            raise ScrapeCheck("You already scrape the links!")
        else:
            days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            print(f"{'|||||  *** Scrape Links ***  |||||':^40}")

            for day in days:
                start = time.time()

                print("|" + "-"*38 + "|")
                print(f"{'|||||  * processing ' + day + '... *  |||||':^40}")
                DAY_PATH = self.base_path + "?tab=" + day
                link = []

                driver = webdriver.Chrome(options=self.options)
                driver.get(DAY_PATH)
                wait = WebDriverWait(driver, timeout=30)  # Prevent session exception
                # Title area class name
                content = wait.until(EC.presence_of_element_located((By.ID, "content")))
                title_info = content.find_elements(By.CLASS_NAME, "ContentTitle__title_area--x24vt")
                for e in title_info:
                    link.append(e.get_attribute("href"))

                self.links.append(link)
                end = time.time()
                print(f"Elapsed time: {end - start:.2f}sec")
            self.is_scraped = True

    def get_links(self):
        return self.links

    def create_raw_database(self):

        # create a rank db
        rank_db = self.create_a_rank_database()

        n = len(self.links)
        count = 0

    def __len__(self):
        size = [len(links) for links in self.links]
        return size

    def create_a_rank_database(self):
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

        rank_database = pd.DataFrame()
        print(f"{'|||||  *** Create a rank database ***  |||||':^50}")

        for day in days:
            start = time.time()

            pop_link = []
            view_link = []
            rate_link = []

            pop_db = pd.DataFrame()
            view_db = pd.DataFrame()
            rate_db = pd.DataFrame()

            print("|" + "-"*48 + "|")
            print(f"{'|||||  * processing ' + day + '... *  |||||':^50}")
            DAY_PATH = self.base_path + "?tab=" + day

            driver = webdriver.Chrome(options=self.options)
            driver.get(DAY_PATH)
            wait = WebDriverWait(driver, timeout=30)

            # rank by pop
            pop = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                "//*[@id='content']/div[1]/div/div[2]/button[1]")))
            pop.click()
            content = driver.find_element(By.ID, "content")
            Link_Info = content.find_elements(By.CLASS_NAME, "ContentTitle__title_area--x24vt")
            for i, link in enumerate(Link_Info):
                pop_link.append((i + 1, link.get_attribute("href")))

            # rank by view
            view = wait.until(EC.presence_of_element_located((By.XPATH,
                                                             "//*[@id='content']/div[1]/div/div[2]/button[3]")))
            view.click()
            content = driver.find_element(By.ID, "content")
            Link_Info = content.find_elements(By.CLASS_NAME, "ContentTitle__title_area--x24vt")
            for i, link in enumerate(Link_Info):
                view_link.append((i + 1, link.get_attribute("href")))

            # rank by rate
            rate = wait.until(EC.presence_of_element_located((By.XPATH,
                                                             "//*[@id='content']/div[1]/div/div[2]/button[4]")))
            rate.click()
            content = driver.find_element(By.ID, "content")
            Link_Info = content.find_elements(By.CLASS_NAME, "ContentTitle__title_area--x24vt")
            for i, link in enumerate(Link_Info):
                rate_link.append((i + 1, link.get_attribute("href")))

            sorted_by_pop = pd.DataFrame(pop_link,
                                         columns=["Popularity", "Link"])
            sorted_by_view = pd.DataFrame(view_link,
                                          columns=["View", "Link"])
            sorted_by_rate = pd.DataFrame(rate_link,
                                          columns=["Rate", "Link"])
            merged = pd.merge(sorted_by_pop, sorted_by_view, on="Link")
            merged = pd.merge(merged, sorted_by_rate, on="Link")

            rank_database = pd.concat([rank_database, merged])
            end = time.time()
            print(f"Elapsed time: {end - start:.2f}s")

        return rank_database

