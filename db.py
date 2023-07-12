from typing import AsyncGenerator, Any

from databases.core import Connection, Database
from settings import postgre_url
from models import *
import databases.backends.postgres
from utils import get_password_hash
from passlib.hash import bcrypt

databases.backends.postgres.Record.__iter__ = lambda self: iter(self._row)


async def get_session() -> AsyncGenerator[Connection, Any]:
    """Return DB session"""

    async with Database(postgre_url) as db, db.connection() as conn:
        yield conn


async def authorize(authorization: Authorization, required_role: str, session: Connection) -> User:
    """
    Checks equivalence of given password hash and hash from database
    :param session: DB connection session
    :param authorization: login and password
    :param required_role:
    :return: models.User
    """
    user = await get_user_by_login(login=authorization.login, session=session)
    if not user:
        return False
    if not user.role == required_role:
        return False
    check = bcrypt.verify(secret=authorization.password, hash=user.password_hash)
    if check:
        return user


async def create_tables(session: Connection):
    query = '''CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY ,
            email VARCHAR(50),
            login VARCHAR(50) UNIQUE ,
            password_hash VARCHAR(100),
            role VARCHAR(50),
            active BOOLEAN DEFAULT TRUE);'''
    await session.execute(query)
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
    await session.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS genres(
            id SERIAL PRIMARY KEY,
            name VARCHAR(20) UNIQUE);'''
    await session.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS authors(
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE);'''
    await session.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS publishers(
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE);'''
    await session.execute(query)


async def get_user_by_id(user_id: int, session: Connection) -> User:
    query = '''SELECT * FROM users WHERE id = :id'''
    result = await session.fetch_one(query=query, values={'id': user_id})
    return User.from_orm(result) if result else None


async def get_user_by_login(login: str, session: Connection) -> User:
    query = '''SELECT * FROM users WHERE login = :login;'''
    result = await session.fetch_one(query=query, values={'login': login})
    return User.from_orm(result) if result else None


async def get_users(session: Connection) -> list[User]:
    query = '''SELECT * FROM users;'''
    result = await session.fetch_all(query=query)
    users = [User.from_orm(user_data) for user_data in result]
    return users


async def insert_user(user_data: NewUserData, session: Connection):
    query = '''INSERT INTO users(email, login, password_hash, role) VALUES 
    (:email, :login, :password, :role);'''
    values = {'email': user_data.email,
              'login': user_data.login,
              'password': get_password_hash(user_data.password),
              'role': user_data.role}
    await session.execute(query=query, values=values)


async def update_user(user_data: User, session: Connection):
    query = '''UPDATE users SET email = :email, login = :login, password_hash = :password,
    active = :active WHERE id = :id;'''
    values = {'email': user_data.email,
              'login': user_data.login,
              'password': get_password_hash(user_data.password_hash),
              'active': user_data.active,
              'id': user_data.id}
    await session.execute(query=query, values=values)


async def delete_user(user_id: int, session: Connection):
    query = '''DELETE FROM users WHERE id = :id'''
    await session.execute(query, {'id': user_id})


async def get_book_by_id(book_id: int, session: Connection) -> Book:
    query = '''SELECT * FROM books WHERE id = :id'''
    result = await session.fetch_one(query=query, values={'id': book_id})
    return Book.from_orm(result) if result else None


async def get_book_by_name(book_name: str, session: Connection) -> Book:
    query = '''SELECT * FROM books WHERE name = :name'''
    result = await session.fetch_one(query=query, values={'name': book_name})
    return Book.from_orm(result) if result else None


async def search_books(session: Connection, filter_name: str = None, filter_value: int = None) -> list[Book]:
    if filter_name and filter_value:
        query = '''SELECT * FROM books WHERE :filter_name = :value;'''
        result = await session.fetch_all(query=query, values={'value': filter_value, 'filter_name': filter_name})
    else:
        query = '''SELECT * FROM books;'''
        result = await session.fetch_all(query=query)
    result = [Book.from_orm(item) for item in result]
    return result


async def insert_book(book_data: NewBookData, session: Connection):
    query = '''INSERT INTO books(name, author_id, publisher_id, genre_id) 
    VALUES(:name, :author_id, :publisher_id, :genre_id);'''
    values = {
        'name': book_data.name,
        'author_id': book_data.author_id,
        'publisher_id': book_data.publisher_id,
        'genre_id': book_data.genre_id
    }
    await session.execute(query=query, values=values)


async def update_book(book_data: Book, session: Connection):
    query = '''UPDATE books SET reserved_datetime = :reserved_datetime, reserver_id = :reserver_id,
    in_stock = :in_stock, owner_id = :owner_id WHERE id = :id;'''
    values = {
        'reserved_datetime': book_data.reserved_datetime,
        'reserver_id': book_data.reserved_user_id,
        'in_stock': book_data.in_stock,
        'owner_id': book_data.owner_id,
        'id': book_data.id
    }
    await session.execute(query=query, values=values)


async def delete_book(book_id: int, session: Connection):
    query = f'''DELETE FROM books WHERE id = :id'''
    await session.execute(query=query, values={'id': book_id})


async def get_genre_by_id(genre_id: int, session: Connection) -> Genre:
    query = '''SELECT * FROM genres WHERE id = :id;'''
    result = await session.fetch_one(query=query, values={'id': genre_id})
    return Genre.from_orm(result) if result else None


async def get_or_insert_genre(genre_name: str, session: Connection) -> Genre:
    query = '''SELECT * FROM genres WHERE name = :name;'''
    result = await session.fetch_one(query, values={'name': genre_name})
    if not result:
        query = '''INSERT INTO genres (name) VALUES (:name) RETURNING *;'''
        result = await session.fetch_one(query=query, values={'name': genre_name})
    return Genre.from_orm(result)


async def get_author_by_id(author_id: int, session: Connection) -> Author:
    query = '''SELECT * FROM authors WHERE id = :id;'''
    result = await session.fetch_one(query=query, values={'id': author_id})
    return Author.from_orm(result) if result else None


async def get_or_insert_author(author_name: str, session: Connection) -> Author:
    query = '''SELECT * FROM authors WHERE name = :name;'''
    result = await session.fetch_one(query, values={'name': author_name})
    if not result:
        query = '''INSERT INTO authors (name) VALUES (:name) RETURNING *;'''
        result = await session.fetch_one(query=query, values={'name': author_name})
    return Author.from_orm(result)


async def get_publisher_by_id(publisher_id: int, session: Connection) -> Publisher:
    query = '''SELECT * FROM publishers WHERE id = :id;'''
    result = await session.fetch_one(query=query, values={'id': publisher_id})
    return Publisher.from_orm(result) if result else None


async def get_or_insert_publisher(publisher_name: str, session: Connection) -> Publisher:
    query = '''SELECT * FROM publishers WHERE name = :name;'''
    result = await session.fetch_one(query, values={'name': publisher_name})
    if not result:
        query = '''INSERT INTO publishers (name) VALUES (:name) RETURNING *;'''
        result = await session.fetch_one(query=query, values={'name': publisher_name})
    return Publisher.from_orm(result)