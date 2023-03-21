import array
import string
import traceback
import pyodbc
import datetime
from user_info import UserInfo
from config import DefaultConfig
from book_detail import BookDetail


class DatabaseInterface:
    SERVER = DefaultConfig.SERVER
    DATABASE = DefaultConfig.DATABASE
    USERNAME = DefaultConfig.USERNAME
    PASSWORD = DefaultConfig.PASSWORD
    DRIVER = '{ODBC Driver 18 for SQL Server}'
    CONNECTIONSTRING = 'DRIVER=' + DRIVER + ';SERVER=tcp:' + SERVER + ',1433;DATABASE=' + DATABASE + ';UID=' + USERNAME + ';PWD=' + PASSWORD + ";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30"
    # =========QUERY SQL===================
    SEARCH_USER_BY_EMAIL = "SELECT email FROM dbo.users WHERE [email] = ?"
    INSERT_USER = "INSERT INTO dbo.users([email],[pwd],[firstName],[lastName]) VALUES (?,?,?,?)"
    GET_PASSWORD = "SELECT pwd FROM dbo.users WHERE [email] = ?"
    FIND_STARRED_BOOK = "SELECT book.isbn,title,publishedDate,description,image from book,users,bookStarred where users.email = ? and users.email = bookStarred.email and book.isbn = bookStarred.isbn"
    GET_COUNTER_SEARCHED_BOOK = "SELECT counter from book,searchedBook where book.isbn = ? and book.isbn = searchedBook.isbn"
    GET_BOOK = "SELECT isbn,title,publishedDate,description,image from book where book.isbn = ?"

    # =========QUERY SQL===================

    @staticmethod
    def insert_user(email, firstname, lastname, password):
        try:
            with pyodbc.connect(DatabaseInterface.CONNECTIONSTRING) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(DatabaseInterface.SEARCH_USER_BY_EMAIL, email)
                    row = cursor.fetchall()
                    if len(row) > 0:
                        return False
                    cursor.execute(DatabaseInterface.INSERT_USER,
                                   email,
                                   password, firstname, lastname)
                    return True
        except:
            traceback.print_exc()
            return False

    @staticmethod
    def get_pwd(email):
        try:
            with pyodbc.connect(DatabaseInterface.CONNECTIONSTRING) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(DatabaseInterface.GET_PASSWORD, email)
                    row = cursor.fetchall()

                    return row[0][0]
        except:
            traceback.print_exc()
            return False

    @staticmethod
    def login(email):
        try:
            with pyodbc.connect(DatabaseInterface.CONNECTIONSTRING) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT email,firstName,lastName FROM dbo.users WHERE [email] = ?", email)
                    row = cursor.fetchall()
                    if len(row) == 0:
                        return False
                    email = row[0][0]
                    firstName = row[0][1]
                    lastName = row[0][2]
                    libri = DatabaseInterface._getStarredBook(email)
                    user = UserInfo(email=email, firstName=firstName, lastName=lastName, starredBook=libri)
                    return user
        except:
            traceback.print_exc()
            return False

    @staticmethod
    def _getStarredBook(email) -> array:
        try:
            with pyodbc.connect(DatabaseInterface.CONNECTIONSTRING) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(DatabaseInterface.FIND_STARRED_BOOK, email)
                    rows = cursor.fetchall()
                    if len(rows) == 0:
                        return []
                    libri = []
                    for row in rows:
                        libro = BookDetail(row[0], row[1], row[2], row[3], row[4])
                        libri.append(libro)
                    return libri
        except:
            traceback.print_exc()
            return False

    @staticmethod
    def delete_account(email):
        try:
            with pyodbc.connect(DatabaseInterface.CONNECTIONSTRING) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM dbo.users WHERE [email] = ?", email)
                    return True
        except:
            traceback.print_exc()
            return False

    @staticmethod
    def addSearchedBook(book: BookDetail) -> bool:
        addbookflag = True
        try:
            with pyodbc.connect(DatabaseInterface.CONNECTIONSTRING) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(DatabaseInterface.GET_COUNTER_SEARCHED_BOOK, book.isbn)
                    row = cursor.fetchall()
                    cursor.execute(DatabaseInterface.GET_BOOK, book.isbn)
                    booksql = cursor.fetchall()
                    if len(booksql) != 1:
                        addbookflag = DatabaseInterface._addBook(book)
                    if len(row) == 0 and addbookflag:
                        addbookcounterflag = DatabaseInterface._addCounterBook(book)
                        if addbookcounterflag:
                            return True
                    if len(row) == 1:
                        counter = row[0][0]
                        addincrementflag = DatabaseInterface._incrmentCountBook(book, counter)
                        if addincrementflag:
                            return True
                    return False
        except:
            traceback.print_exc()
            return False

    @staticmethod
    def _incrmentCountBook(book: BookDetail, counter: int):
        try:
            with pyodbc.connect(DatabaseInterface.CONNECTIONSTRING) as conn:
                with conn.cursor() as cursor:
                    counter += 1
                    cursor.execute("UPDATE dbo.searchedBook SET counter = ? WHERE isbn = ?", counter, book.isbn)
                    return True
        except:
            traceback.print_exc()
            return False

    @staticmethod
    def _addCounterBook(book: BookDetail) -> bool:
        try:
            with pyodbc.connect(DatabaseInterface.CONNECTIONSTRING) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO dbo.searchedBook([isbn]) VALUES (?)",
                        book.isbn)
                    return True
        except Exception:
            traceback.print_exc()
            return False

    @staticmethod
    def _addBook(book: BookDetail) -> bool:
        try:
            with pyodbc.connect(DatabaseInterface.CONNECTIONSTRING) as conn:
                with conn.cursor() as cursor:
                    pd = str(book.publishedDate).replace("('", "").replace("',)", "")
                    description = str(book.description).replace("('", "").replace("',)", "")
                    datesplit = pd.split("T")[0].split("-")
                    date = datetime.date(int(datesplit[0]), int(datesplit[1]), int(datesplit[2]))
                    cursor.execute(
                        "INSERT INTO book([isbn],[title],[publishedDate],[description],[image]) VALUES (?,?,?,?,?)",
                        book.isbn,
                        book.title, date, description, book.image)
                    return True
        except:
            traceback.print_exc()
            return False

    @staticmethod
    def _checkBookIsExist(book) -> bool:
        try:
            with pyodbc.connect(DatabaseInterface.CONNECTIONSTRING) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * from book where book.isbn = ?", book.isbn)
                    row = cursor.fetchall()
                    if len(row) == 0:
                        return False
                    return True
        except:
            traceback.print_exc()
            return False

    @staticmethod
    def addStarredBook(user: UserInfo, book: BookDetail):
        try:
            with pyodbc.connect(DatabaseInterface.CONNECTIONSTRING) as conn:
                with conn.cursor() as cursor:
                    if not DatabaseInterface._checkBookIsExist(book):
                        if not DatabaseInterface._addBook(book):
                            return False
                    cursor.execute(
                                "INSERT INTO bookStarred([isbn],[email]) VALUES (?,?)",
                                book.isbn, user.email)
                    return True
        except:
            traceback.print_exc()
            return False
