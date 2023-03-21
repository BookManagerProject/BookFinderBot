# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import array
import string


class BookDetail:
    def __init__(
            self,
            isbn: string,
            tile: string,
            publishedDate: string,
            description: string,
            image: string
    ):
        self.isbn = isbn
        self.title = tile
        self.publishedDate = publishedDate,
        self.description = description,
        self.image = image
