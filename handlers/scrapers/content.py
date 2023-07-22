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
