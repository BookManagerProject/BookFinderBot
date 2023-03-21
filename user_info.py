from book_detail import BookDetail


class UserInfo:
    def __init__(self, email=None, password=None, firstName=None, lastName=None, starredBook=None):
        self.email = email
        self.password = password
        self.firstName = firstName
        self.lastName = lastName
        self.starredBook = starredBook

    def get_user_info(self):
        return f"{self.email} {self.firstName} {self.lastName} {self.starredBook}"

    def checkIfBookIsStarred(self, book: BookDetail):
        for booklist in self.starredBook:
            if booklist.isbn == book.isbn:
                return True
        return False
