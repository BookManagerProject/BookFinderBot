# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import array


class BookDetail:
    def __init__(
            self,
            titleorisbn: str = None,
            index: str = None,
            book: array = None
    ):
        self.titleorisbn = titleorisbn
        self.index = index
        self.book = book
