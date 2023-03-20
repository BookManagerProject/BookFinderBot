import array

import requests


class GoogleBooksAPI:
    BASE_URL = 'https://www.googleapis.com/books/v1/'

    def __init__(self):
        self.results = []

    def search_by_isbn(self, isbn) -> dict:
        url = f'{self.BASE_URL}volumes?q=isbn:{isbn}'
        response = requests.get(url)
        self.results.append(self._parse_response(response))
        return self._parse_response(response)[0]

    def search_by_title(self, title) -> array:
        url = f'{self.BASE_URL}volumes?q=intitle:{title}'
        response = requests.get(url)
        self.results = self._parse_response(response)
        return self._parse_response(response)

    def _parse_response(self, response):
        results = response.json()['items']
        books = []
        for result in results:
            book = {
                'isbn': result['volumeInfo'].get('industryIdentifiers', [])[0].get('identifier', '') if result[
                    'volumeInfo'].get('industryIdentifiers', []) else '',
                'title': result['volumeInfo'].get('title', ''),
                'publishedDate': result['volumeInfo'].get('publishedDate', ''),
                'description': result['volumeInfo'].get('description', ''),
                'pageCount': result['volumeInfo'].get('pageCount', ''),
                'categories': result['volumeInfo'].get('categories', []),
                'imageLinks': result['volumeInfo'].get('imageLinks', {}),
                'previewLink': result['volumeInfo']["imageLinks"]["thumbnail"],
                'infoLink': result['volumeInfo'].get('infoLink', '')
            }
            books.append(book)
        return books
