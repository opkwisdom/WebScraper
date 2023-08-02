"""
WebtoonScraper Class

method
1. scrape_links(self) : scrape the links for the day of the week
                        parameter day must be in one of the following formats
                        ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
2. get_links(self) : get the scraped links of the class instance
3. create_database(self) : create database from sub-method 3.1 & 3.2
    3.1. create_feature_database: extract feature information about each webtoon and make sub database
    3.2. create_rank_database: extract rank information and make sub database
4. set_driver_options(self) : set the WebDriver options
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import os
import time
import pandas as pd
import pyperclip


# Exception class
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
        self.options.add_argument('--headless')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        # set User-Agent for preventing access blocked
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)" +
                                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        # prevent webdriver from closing immediately
        self.options.add_experimental_option("detach", True)

    # scrape webtoon links according to given day
    def scrape_links(self):
        if self.is_scraped:
            raise ScrapeCheck("You already scrape the links!")
        else:
            days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            print(f"{'|||||  *** Scrape Links ***  |||||':^40}")

            total_time = 0
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
                print(f"Elapsed time: {end - start:.2f}sec / length: {len(link)}")
                total_time += round(end - start, 2)
            self.is_scraped = True

            self.links = sum(self.links, [])
            # remove duplicate rows
            self.links = list(set(self.links))

            print("|" + "-" * 38 + "|")
            print(f"Total elapsed time: {total_time:.2f}s")
            print()

    def get_links(self):
        return self.links

    def set_links(self, links):
        self.links = links

    def create_database(self):
        if os.path.exists('WebScraper/rank_db.csv') and os.path.exists('WebScraper/feature_db.csv'):
            rank_db = pd.read_csv('WebScraper/rank_db.csv')
            feature_db = pd.read_csv('WebScraper/feature_db.csv')
            full_db = pd.merge(feature_db, rank_db, on="Link")
        else:
            # create rank db
            rank_db = self.create_rank_database()
            # create feature db
            feature_db = self.create_feature_database()

            full_db = pd.merge(feature_db, rank_db, on="Link")
        return full_db

    def __len__(self):
        size = [len(links) for links in self.links]
        return sum(size)

    # extract feature information about each webtoon and make sub database
    def create_feature_database(self):
        total_time = 0

        links = self.links
        size = len(links)

        features = []

        print(f"{'|||||  *** Create a feature database ***  |||||':^50}")
        print()
        for i, link in enumerate(links):
            start = time.time()

            options = self.options
            options.headless = True
            driver = webdriver.Chrome(options=options)
            driver.get(link)
            # Wait up to 10 seconds for the webpage to load
            driver.implicitly_wait(10)

            print(f"{'|||||  * Process: Webtoon ' + str(i+1) + 'th/' + str(size) + 'th *  |||||':^50}")

            # In case of adult authentication
            if driver.title == '네이버 : 로그인':
                driver.quit()

                options.headless = False
                driver = webdriver.Chrome(options=options)
                # account for adult authentication
                driver.get(link)
                driver.implicitly_wait(10)

                with open("WebScraper/Authentication.txt", "r") as f:
                    user_info = f.readlines()
                user_info = [info.strip() for info in user_info]

                ID = user_info[0]
                PW = user_info[1]

                id_input = driver.find_element(By.ID, "id")
                id_input.click()
                pyperclip.copy(ID)  # copy & paste for auto-input protection character bypass
                id_input.send_keys(Keys.CONTROL, 'v')
                time.sleep(1)
                pw_input = driver.find_element(By.ID, "pw")
                pw_input.click()
                pyperclip.copy(PW)  # copy & paste for auto-input protection character bypass
                pw_input.send_keys(Keys.CONTROL, 'v')
                time.sleep(1)

                login_btn = driver.find_element(By.ID, "log.login")
                login_btn.click()
                time.sleep(1)

                dont_save = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "new.dontsave")))
                dont_save.click()

            # Title
            title = driver.find_elements(By.CLASS_NAME, "EpisodeListInfo__title--mYLjC")[0].text

            # Writer, Painter
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

            features.append([link, title, writer, painter, serial_date, serial_rate, genre,
                             tags, likes, total_publishes, summary])
            driver.quit()

            end = time.time()
            print(f"Current scraped webtoon: {title}")
            print(f"Elapsed time: {end - start:.2f}s")
            total_time += round(end - start, 2)
            print(f"Total Elapsed_time: {total_time:.2f}s")
            print("|" + "-" * 48 + "|")
            print()

        feature_database = pd.DataFrame(features,
                                        columns=["Link", "Title", "Writer", "Painter", "Serial_Date", "Serial_Rate",
                                                 "Genre", "Tags", "Likes", "Total_Publishes", "Summary"])
        print()
        return feature_database

    # extract rank information and make sub database
    def create_rank_database(self):
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

        rank_database = pd.DataFrame()
        print(f"{'|||||  *** Create a rank database ***  |||||':^50}")
        print()

        total_time = 0
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
            wait = WebDriverWait(driver, timeout=40)

            # rank by pop
            pop = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                "//*[@id='content']/div[1]/div/div[2]/button[1]")))
            pop.click()
            # WebDriverWait until loading the page
            time.sleep(1)
            content = driver.find_element(By.ID, "content")
            Link_Info = content.find_elements(By.CLASS_NAME, "ContentTitle__title_area--x24vt")
            for i, link in enumerate(Link_Info):
                pop_link.append((i + 1, link.get_attribute("href")))

            # rank by view
            view = wait.until(EC.presence_of_element_located((By.XPATH,
                                                             "//*[@id='content']/div[1]/div/div[2]/button[3]")))
            view.click()
            # WebDriverWait until loading the page
            time.sleep(1)
            content = driver.find_element(By.ID, "content")
            Link_Info = content.find_elements(By.CLASS_NAME, "ContentTitle__title_area--x24vt")
            for i, link in enumerate(Link_Info):
                view_link.append((i + 1, link.get_attribute("href")))

            # rank by rate
            rate = wait.until(EC.presence_of_element_located((By.XPATH,
                                                             "//*[@id='content']/div[1]/div/div[2]/button[4]")))
            rate.click()
            # WebDriverWait until loading the page
            time.sleep(1)
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
            print(f"df1 shape: {sorted_by_pop.shape} / df2 shape: {sorted_by_view.shape} / df3 shape: {sorted_by_rate.shape}")

            total_time += round(end - start, 2)
        # drop duplicate rows
        rank_database = rank_database.drop_duplicates(subset=["Link"])
        print("|" + "-"*48 + "|")
        print(f"Total Elapsed time: {total_time:.2f}s")
        print()
        return rank_database