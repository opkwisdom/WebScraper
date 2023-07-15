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

            for day in days:
                print("-"*32)
                print(f"|||||  processing {day}...  |||||")
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

    def get_links(self):
        return self.links

    def make_raw_database(self):
        n = len(self.links)
        count = 0

        driver = self.driver
        WebDriverWait(driver, timeout=10)

        for link in self.links:
            start = time.clock()
            count += 1
            print(f'-*10 {count}/{n} -*10')

            driver.get(link)

            driver.quit()
            end = time.clock()
            print(f'Scrapping time: {end - start}s')

    def __len__(self):
        return len(self.links)

    def sorted_database(self):
        days = ["?tab=mon", "?tab=tue", "?tab=wed", "?tab=thu", "?tab=fri", "?tab=sat", "?tab=sun"]
        DAYS_PATH = [(path + day) for path, day in zip([self.base_path] * 7, days)]

        driver = self.driver
        WebDriverWait(driver, timeout=200)

        famous = driver.find_elements(By.XPATH, "//*[@id='content']/div[1]/div/div[2]/button[1]")
        view = driver.find_elements(By.XPATH, "//*[@id='content']/div[1]/div/div[2]/button[3]")
        rate = driver.find_elements(By.XPATH, "//*[@id='content']/div[1]/div/div[2]/button[4]")

        link_by_method = []
        method = [famous, view, rate]

        driver.close()

        rank_database = pd.DataFrame()

        for j, PATH in enumerate(DAYS_PATH):
            print(f"----------{j}/7----------")
            start = time.time()
            for sort in method:
                driver = self.driver
                WebDriverWait(driver, timeout=200)
                driver.get(PATH)

                sort.click()
                link = []

                Content = driver.find_element(By.ID, "content")

                Link_Info = Content.find_elements(By.CLASS_NAME, "ContentTitle__title_area--x24vt")
                for i, link in enumerate(Link_Info):
                    link.append((i + 1, link.get_attribute("href")))
                link_by_method.append(link)

            sorted_by_pop = pd.DataFrame(link_by_method[0],
                                         columns=["Popularity", "Link"])
            sorted_by_view = pd.DataFrame(link_by_method[1],
                                          columns=["View", "Link"])
            sorted_by_rate = pd.DataFrame(link_by_method[2],
                                          columns=["Rate", "Link"])
            merged = pd.merge(sorted_by_pop, sorted_by_view, on="Link")
            merged = pd.merge(merged, sorted_by_rate, on="Link")

            rank_database = pd.concat(rank_database, merged)
            end = time.time()
            print(f"Elapsed time: {end - start:.2f}s")

        return rank_database



