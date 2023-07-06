import settings
from models import Book, User, Genre, Author, Publisher
import databases.backends.postgres
databases.backends.postgres.Record.__iter__ = lambda self: iter(self._row)


database = databases.Database(settings.postgre_url)


async def create_tables():
    query = '''CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY ,
            email VARCHAR(50),
            login VARCHAR(50) UNIQUE ,
            password VARCHAR(50),
            role VARCHAR(50),
            active BOOLEAN);'''
    await database.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS books(
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE,
            author_id INTEGER,
            publisher_id INTEGER,
            genre_id INTEGER,
            reserved_datetime INTEGER DEFAULT 0,
            reserver_id INTEGER DEFAULT NULL,
            in_stock BOOLEAN DEFAULT TRUE, 
            owner_id INTEGER DEFAULT NULL);'''
    await database.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS genres(
            id SERIAL PRIMARY KEY,
            name VARCHAR(20) UNIQUE);'''
    await database.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS authors(
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE);'''
    await database.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS publisher(
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE);'''
    await database.execute(query)


async def get_user(user_id=None, login=None) -> User:
    if user_id:
        query = '''SELECT * FROM users WHERE id = :id;'''
        result = await database.fetch_all(query=query, values={'id': user_id})
        if result:
            return User(*result[0])
    if login:
        query = '''SELECT * FROM users WHERE login = :login;'''
        result = await database.fetch_all(query=query, values={'login': login})
        if result:
            return User(*result[0])
    return None


async def get_users() -> list[User]:
    query ='''SELECT * FROM users;'''
    result = await database.fetch_all(query=query)
    users = [User(*user_data) for user_data in result]
    return users

async def insert_user(user_data: dict):
    query = '''INSERT INTO users(email, login, password, role, active) VALUES 
    (:email, :login, :password, :role, TRUE);'''
    await database.execute(query=query, values=user_data)


async def update_user(user_data: dict):
    query = '''UPDATE users SET email = :email, login = :login, password = :password, active = :active WHERE id = :id;'''
    await database.execute(query=query, values=user_data)


async def delete_user(user_id: int):
    query = '''DELETE FROM users WHERE id = :id'''
    await database.execute(query, {'id': user_id})


async def get_book(book_id=None, book_name=None) -> Book:
    if book_id:
        query = '''SELECT * FROM books WHERE id = :id;'''
        result = await database.fetch_all(query=query, values={'id': book_id})
        if result:
            return Book(*result[0])
    if book_name:
        query = '''SELECT * FROM books WHERE name = :name;'''
        result = await database.fetch_all(query=query, values={'name': book_name})
        if result:
            return Book(*result[0])
    return None


async def search_books(author_id=None, genre_id=None, publisher_id=None) -> list[Book]:
    filters = False
    if author_id:
        filters = True
        filter_name = 'author_id'
        value = author_id
    elif genre_id:
        filters = True
        filter_name = 'genre_id'
        value = genre_id
    elif publisher_id:
        filters = True
        filter_name = 'publisher_id'
        value = publisher_id
    if filters:
        query = '''SELECT * FROM books WHERE :filter_name = :value;'''
        result = await database.fetch_all(query=query, values={'value': value, 'filter_name': filter_name})
    else:
        query = '''SELECT * FROM books;'''
        result = await database.fetch_all(query=query)
    result = [Book(*item) for item in result]
    return result


async def insert_book(book_data: dict):
    query = '''INSERT INTO books(name, author_id, publisher_id, genre_id,) VALUES(:name, :author, :publisher, :genre_id);'''
    await database.execute(query=query, values=book_data)


async def update_book(book_data: dict):
    query = '''UPDATE books SET reserved_datetime = :reserved_datetime, reserver_id = :reserver_id, in_stock = :in_stock, owner_id = :owner_id WHERE id = :id;'''
    await database.execute(query=query, values=book_data)


async def delete_book(book_id: int):
    query = f'''DELETE FROM books WHERE id = :id'''
    await database.execute(query=query, values={'id': book_id})


async def get_genre(genre_id=None, genre_name=None) -> Genre:
    if genre_id:
        query = '''SELECT * FROM genres WHERE id = :id;'''
        result = await database.fetch_all(query=query, values={'id': genre_id})
        if result:
            return Genre(*result[0])
    if genre_name:
        query = '''SELECT * FROM genres WHERE name = :name;'''
        result = await database.fetch_all(query=query, values={'name': genre_name})
        if result:
            return Genre(*result[0])
    return None


async def insert_genre(name: str) -> Genre:
    query = '''INSERT INTO genres(name) VALUES (:name);'''
    await database.execute(query=query, values={'name': name})
    return await get_genre(genre_name=name)


async def get_author(author_id=None, author_name=None) -> Author:
    if author_id:
        query = '''SELECT * FROM authors WHERE id = :id;'''
        result = await database.fetch_all(query=query, values={'id': author_id})
        if result:
            return Author(*result[0])
    if author_name:
        query = '''SELECT * FROM authors WHERE name = :name;'''
        result = await database.fetch_all(query=query, values={'name': author_name})
        if result:
            return Author(*result[0])
    return None


async def insert_author(name: str) -> Author:
    query = '''INSERT INTO authors(name) VALUES (:name);'''
    await database.execute(query=query, values={'name': name})
    return await get_author(author_name=name)


async def get_publisher(publisher_id=None, publisher_name=None) -> Publisher:
    if publisher_id:
        query = '''SELECT * FROM publishers WHERE id = :id;'''
        result = await database.fetch_all(query=query, values={'id': publisher_id})
        if result:
            return Publisher(*result[0])
    if publisher_name:
        query = '''SELECT * FROM publishers WHERE name = :name;'''
        result = await database.fetch_all(query=query, values={'name': publisher_name})
        if result:
            return Publisher(*result[0])
    return None


async def insert_publisher(name: str) -> Publisher:
    query = '''INSERT INTO publishers(name) VALUES (:name);'''
    await database.execute(query=query, values={'name': name})
    return await get_publisher(publisher_name=name)