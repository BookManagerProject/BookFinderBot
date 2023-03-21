DROP TABLE IF EXISTS searchedBook;
DROP TABLE IF EXISTS bookStarred;
DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS users;

CREATE TABLE users(
	email varchar(255) NOT NULL,
	pwd varchar(255) NOT NULL,
	firstName varchar(255),
	lastName varchar(255),
	PRIMARY KEY (email)
)

CREATE TABLE book(
    isbn varchar(255),
    title varchar(255),
    publishedDate date,
    description text,
    image varchar(255),
    PRIMARY KEY (isbn)
)

CREATE TABLE bookStarred(
	isbn varchar(255) NOT NULL,
	email varchar(255) NOT NULL,
	PRIMARY KEY (isbn,email),
	FOREIGN KEY (email) REFERENCES [dbo].[users](email),
	FOREIGN KEY (isbn) REFERENCES [dbo].[book](isbn)
)

CREATE TABLE searchedBook(
    isbn varchar(255) NOT NULL,
    counter int default 1,
    primary key (isbn),
    FOREIGN KEY (isbn) REFERENCES [dbo].[book](isbn)
)

--SELECT counter from book,searchedBook
--where book.isbn = ? and book.isbn = searchedBook.isbn

--SELECT book.isbn,title,publishedDate,description,image from book,users,bookStarred
--where users.email = bookStarred.email and book.isbn = bookStarred.isbn

INSERT INTO users (email, pwd, firstName, lastName)
VALUES ('test@test.com', '$2b$12$plnxhvXp0eR4g0BMTB3tVexXNOK5atAr6r3lBz9gxBt.wvlK7RqQq', 'Nome', 'Cognome');
--passowrd test