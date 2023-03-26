import difflib

import requests

from config import DefaultConfig


class CercaLibro:
    SEARCH_ENDPOINT = 'https://api.bing.microsoft.com/v7.0/search'

    def __init__(self):
        self.headers = {"Ocp-Apim-Subscription-Key": DefaultConfig.BING_SEARCH_API_KEY}

    def get_book_by_name(self, book_name):
        query = f"{book_name} libro"
        params = {"q": query, "textDecorations": True, "textFormat": "HTML", 'setLang': 'it-IT', 'mkt': 'it-IT'}
        response = requests.get(self.SEARCH_ENDPOINT, headers=self.headers, params=params)
        response.raise_for_status()
        response_results = response.json()
        web_pages = response_results['webPages']
        web_pages_values = web_pages['value']
        list = []
        if len(web_pages_values) > 0:
            for value in web_pages_values:
                list.append(value["name"])
        return self._elimina_simili(list)

    def _elimina_simili(self, lista):
        risultato = []
        for elemento in lista:
            if not any(difflib.SequenceMatcher(None, elemento, x).ratio() > 0.8 for x in risultato):
                risultato.append(elemento)
        return risultato
