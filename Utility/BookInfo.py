import requests
import validators
from bs4 import BeautifulSoup


class BookInfo:
    def __init__(self, url):
        if validators.url(url):
            self.url = url
            self.page = requests.get(url)
            self.soup = BeautifulSoup(self.page.content, "html.parser")

    def getBookName(self):
        results = self.soup.find("p", itemprop="description")
        if len(results) == 1:
            split = results.split(":")
            if len(split) > 1:
                title = split[0]
                return title
        return False
