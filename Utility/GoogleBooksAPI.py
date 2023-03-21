import array

import requests


class GoogleBooksAPI:
    BASE_URL = 'https://www.googleapis.com/books/v1/'

    def __init__(self):
        self.results = []

    def search_by_isbn(self, isbn) -> dict:
        url = f'{self.BASE_URL}volumes?q=isbn:{isbn}'
        response = requests.get(url)
        parsed = self._parse_response(response)
        if parsed is not None:
            self.results.append(self._parse_response(response))
            return self._parse_response(response)[0]
        else:
            return None

    def search_by_title(self, title) -> array:
        url = f'{self.BASE_URL}volumes?q=intitle:{title}'
        response = requests.get(url)
        self.results = self._parse_response(response)
        return self.results

    def _parse_response(self, response):
        json = response.json()
        if json["totalItems"] == 0:
            return None
        results = json['items']
        books = []
        for result in results:
            try:
                thumbmail = result['volumeInfo']["imageLinks"]["thumbnail"]
            except Exception:
                continue
            autori = str(result['volumeInfo'].get('authors', '')).replace("[", "").replace("]", "").replace("'", "")
            book = {
                'isbn': result['volumeInfo'].get('industryIdentifiers', [])[0].get('identifier', '') if result[
                    'volumeInfo'].get('industryIdentifiers', []) else '',
                'title': result['volumeInfo'].get('title', ''),
                'publishedDate': result['volumeInfo'].get('publishedDate', ''),
                'description': result['volumeInfo'].get('description', ''),
                'previewLink': thumbmail,
                'infoLink': result['volumeInfo'].get('infoLink', ''),
                'autori': autori
            }
            books.append(book)
        return books
