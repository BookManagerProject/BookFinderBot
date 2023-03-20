import requests

from Utility.BookInfo import BookInfo
from config import DefaultConfig


class CercaLibro:
    SEARCH_ENDPOINT = 'https://api.bing.microsoft.com/v7.0/search'

    def __init__(self):
        self.headers = {"Ocp-Apim-Subscription-Key": DefaultConfig.BING_SEARCH_API_KEY}

    '''
    Cerca il libro in base al nome o all'isbn
    '''
    def get_book_by_name(self, book_name):
        query = f"{book_name} libro+site:unilibro.it"
        params = {"q": query, "textDecorations": True, "textFormat": "HTML", 'setLang': 'it-IT', 'mkt': 'it-IT'}
        response = requests.get(self.SEARCH_ENDPOINT, headers=self.headers, params=params)
        response.raise_for_status()
        response_results = response.json()
        web_pages = response_results['webPages']
        web_pages_values = web_pages['value']
        if len(web_pages_values) > 1:
            book = BookInfo(web_pages_values[0]["url"])
            print(book.getBookName())
        urls = []
        print(web_pages_values)
        return ""
