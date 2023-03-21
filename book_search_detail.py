# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import array


class BookSearchDetail:
    def __init__(
            self,
            titleorisbn: str = None,
            index: str = None,
            books: array = None
    ):
        self.titleorisbn = titleorisbn
        self.index = index
        self.books = books
