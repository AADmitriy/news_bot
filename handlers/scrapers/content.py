""" # imports for using selenium
from selenium.webdriver.chrome import service, options, webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
"""

import requests
from bs4 import BeautifulSoup
import re


class Content:
    """
    Class for parsing news sites
    """

    def __init__(self, site_url: str, page_url: str,
                 article: str, time='', text='', href=''):
        """
        Sets instance variables for scraping
        Args:
            param site_url: url of news site e.g. https://www.example.ua
            param page_url: path to page with articles e.g. /articles/
            param article:  css selector that must point to articles e.g. div.article_news_example
            param time:     css selector that must point to tag with time data e.g. div.article_time
            param text:     css selector that must point to tag with text data e.g. div.article_header p
            param href:     css selector that must point to tag that contain link to article e.g. div.article_link a
        """
        self.site_url = site_url
        self.page_url = page_url
        self.article_selector = article
        self.time_selector = time
        self.text_selector = text
        self.href_selector = href

    def get_page(self):
        try:
            req = requests.get(self.site_url + self.page_url)

        except requests.exceptions.RequestException:
            return None

        return BeautifulSoup(req.text, 'html.parser')

    """
    def get_page(self):
        chrome_options = options.Options()
        chrome_options.add_argument('--headless')  # this enables selenium run in the background
        chrome_options.add_argument('--log-level=3')  # this reduces the number of log messages

        # here you should set your own path to chromedriver executable
        chrome_service = service.Service(executable_path="C:/chromedriver/chromedriver.exe")

        # creates driver and loads page in the current browser version
        driver = webdriver.WebDriver(options=chrome_options, service=chrome_service)
        driver.get(self.site_url + self.page_url)

        try:
            WebDriverWait(driver, 10).until(  # wait for 10 sec until tag with article appear
                EC.presence_of_element_located((By.CSS_SELECTOR, self.article_selector)))
        except TimeoutException:
            return None
        finally:
            page_source = driver.page_source  # gets source of page
            driver.close()

        return BeautifulSoup(page_source, 'html.parser')
    """

    def safe_get(self, page_obj, selector: str, mode: int):
        """
        Args:
            param page_obj (BeautifulSoup object): page object to parse
            param selector: specifies the path to the tag
            param mode: defines retrieve all tags (0) or retrieve only one (1)
        Return:
            list of tags or one tag
        """
        if not selector:
            return ''

        if mode == 0:
            selected_elems = page_obj.select(selector)
        else:
            selected_elems = page_obj.select_one(selector)

        if selected_elems:
            return selected_elems
        return ''

    def get_articles(self):
        bs = self.get_page()

        if bs is not None:
            # retrieve all articles from bs object using selector
            articles_list = self.safe_get(bs, self.article_selector, 0)
            return articles_list

    def parse(self):
        articles_list = self.get_articles()
        if not articles_list:
            return None

        result_list = []
        for article in articles_list:
            # retrieve data from tags using selectors
            # sets default None value if no data or selector
            time_tag = self.safe_get(article, self.time_selector, 1)
            if time_tag:
                time = time_tag.get_text()
            else:
                time = None

            text_tag = self.safe_get(article, self.text_selector, 1)
            if text_tag:
                text = text_tag.get_text()
            else:
                text = None

            href_tag = self.safe_get(article, self.href_selector, 1)
            if href_tag:
                href = href_tag.attrs['href']

                # expression r'(https?://[\S]+)' mean any string that starts with http:// or https://
                # and in the following part has one or more characters that are not whitespace
                if not re.match(r'(https?://[\S]+)', href):  # checks whether link is absolute
                    href = self.site_url + href  # creates absolute link
            else:
                href = None

            article_data = [time, text, href]
            result_list.append(article_data)

        return result_list
