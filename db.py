from models import *
import databases.backends.postgres
from utils import get_password_hash

databases.backends.postgres.Record.__iter__ = lambda self: iter(self._row)
database = databases.Database(settings.postgre_url)


async def authorize(authorization: Authorization, required_role: str) -> User:
    """
    Checks equivalence of given password hash and hash from database
    :param authorization: login and password
    :param required_role:
    :return: models.User
    """
    user = await get_user_by_login(login=authorization.login)
    password_hash = get_password_hash(authorization.password)
    if not user:
        return False
    check = (user.password == password_hash) and (user.role == required_role)
    if check:
        return user


async def create_tables():
    query = '''CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY ,
            email VARCHAR(50),
            login VARCHAR(50) UNIQUE ,
            password_hash VARCHAR(100),
            role VARCHAR(50),
            active BOOLEAN DEFAULT TRUE);'''
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
    query = '''CREATE TABLE IF NOT EXISTS publishers(
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE);'''
    await database.execute(query)


async def get_user_by_id(user_id: int) -> User:
    query = '''SELECT * FROM users WHERE id = :id'''
    result = await database.fetch_one(query=query, values={'id': user_id})
    return User.from_list(result) if result else None


async def get_user_by_login(login: str) -> User:
    query = '''SELECT * FROM users WHERE login = :login;'''
    result = await database.fetch_one(query=query, values={'login': login})
    return User.from_list(result) if result else None


async def get_users() -> list[User]:
    query = '''SELECT * FROM users;'''
    result = await database.fetch_all(query=query)
    users = [User.from_list(user_data) for user_data in result]
    return users


async def insert_user(user_data: NewUserData):
    query = '''INSERT INTO users(email, login, password_hash, role) VALUES 
    (:email, :login, :password, :role);'''
    values = {'email': user_data.email,
              'login': user_data.login,
              'password': get_password_hash(user_data.password),
              'role': user_data.role}
    await database.execute(query=query, values=values)


async def update_user(user_data: User):
    query = '''UPDATE users SET email = :email, login = :login, password_hash = :password,
    active = :active WHERE id = :id;'''
    values = {'email': user_data.email,
              'login': user_data.login,
              'password': get_password_hash(user_data.password),
              'active': user_data.active,
              'id': user_data.id}
    await database.execute(query=query, values=values)


async def delete_user(user_id: int):
    query = '''DELETE FROM users WHERE id = :id'''
    await database.execute(query, {'id': user_id})


async def get_book_by_id(book_id: int) -> Book:
    query = '''SELECT * FROM books WHERE id = :id'''
    result = await database.fetch_one(query=query, values={'id': book_id})
    return Book.from_list(result) if result else None


async def get_book_by_name(book_name: str) -> Book:
    query = '''SELECT * FROM books WHERE name = :name'''
    result = await database.fetch_one(query=query, values={'name': book_name})
    return Book.from_list(result) if result else None


async def search_books(filter_name: str = None, filter_value: int = None) -> list[Book]:
    if filter_name and filter_value:
        query = '''SELECT * FROM books WHERE :filter_name = :value;'''
        result = await database.fetch_all(query=query, values={'value': filter_value, 'filter_name': filter_name})
    else:
        query = '''SELECT * FROM books;'''
        result = await database.fetch_all(query=query)
    result = [Book.from_list(item) for item in result]
    return result


async def insert_book(book_data: NewBookData):
    query = '''INSERT INTO books(name, author_id, publisher_id, genre_id) 
    VALUES(:name, :author_id, :publisher_id, :genre_id);'''
    values = {
        'name': book_data.name,
        'author_id': book_data.author_id,
        'publisher_id': book_data.publisher_id,
        'genre_id': book_data.genre_id
    }
    await database.execute(query=query, values=values)


async def update_book(book_data: Book):
    query = '''UPDATE books SET reserved_datetime = :reserved_datetime, reserver_id = :reserver_id,
    in_stock = :in_stock, owner_id = :owner_id WHERE id = :id;'''
    values = {
        'reserved_datetime': book_data.reserved_datetime,
        'reserver_id': book_data.reserved_user_id,
        'in_stock': book_data.in_stock,
        'owner_id': book_data.owner_id,
        'id': book_data.id
    }
    await database.execute(query=query, values=values)


async def delete_book(book_id: int):
    query = f'''DELETE FROM books WHERE id = :id'''
    await database.execute(query=query, values={'id': book_id})


async def get_genre_by_id(genre_id: int) -> Genre:
    query = '''SELECT * FROM genres WHERE id = :id;'''
    result = await database.fetch_one(query=query, values={'id': genre_id})
    return Genre.from_list(result) if result else None


async def get_genre_by_name(genre_name: str) -> Genre:
    query = '''SELECT * FROM genres WHERE name = :name;'''
    result = await database.fetch_one(query=query, values={'name': genre_name})
    return Genre.from_list(result) if result else None


async def insert_genre(name: str) -> Genre:
    query = '''INSERT INTO genres(name) VALUES (:name);'''
    await database.execute(query=query, values={'name': name})
    return await get_genre_by_name(genre_name=name)


async def get_author_by_id(author_id: int) -> Author:
    query = '''SELECT * FROM authors WHERE id = :id;'''
    result = await database.fetch_one(query=query, values={'id': author_id})
    return Author.from_list(result) if result else None


async def get_author_by_name(author_name: str) -> Author:
    query = '''SELECT * FROM authors WHERE name = :name;'''
    result = await database.fetch_one(query=query, values={'name': author_name})
    return Author.from_list(result) if result else None


async def insert_author(name: str) -> Author:
    query = '''INSERT INTO authors(name) VALUES (:name);'''
    await database.execute(query=query, values={'name': name})
    return await get_author_by_name(author_name=name)


async def get_publisher_by_id(publisher_id: int) -> Publisher:
    query = '''SELECT * FROM publishers WHERE id = :id;'''
    result = await database.fetch_one(query=query, values={'id': publisher_id})
    return Genre.from_list(result) if result else None


async def get_publisher_by_name(publisher_name: str) -> Publisher:
    query = '''SELECT * FROM publishers WHERE name = :name;'''
    result = await database.fetch_one(query=query, values={'name': publisher_name})
    return Genre.from_list(result) if result else None


async def insert_publisher(name: str) -> Publisher:
    query = '''INSERT INTO publishers(name) VALUES (:name);'''
    await database.execute(query=query, values={'name': name})
    return await get_publisher_by_name(publisher_name=name)
