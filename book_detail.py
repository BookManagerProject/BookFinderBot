# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import string


class BookDetail:
    def __init__(
            self,
            isbn: string,
            tile: string,
            publishedDate: string,
            description: string,
            image: string,
            autori: string
    ):
        self.isbn = str(isbn)
        self.title = str(tile)
        self.publishedDate = publishedDate,
        self.description = str(description),
        self.image = str(image),
        self.autori = str(autori)
