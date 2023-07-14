from typing import AsyncGenerator, Any
from databases.core import Connection, Database
from app.settings import postgre_url
from app.core.schemas import users_schema
from app.core.schemas import books_schema, misc_schema
import databases.backends.postgres
from passlib.hash import bcrypt

databases.backends.postgres.Record.__iter__ = lambda self: iter(self._row)


async def get_session() -> AsyncGenerator[Connection, Any]:
    """Return DB session"""

    async with Database(postgre_url) as db, db.connection() as conn:
        yield conn


async def authorize(authorization: misc_schema.Authorization,
                    required_role: str, session: Connection) -> users_schema.User:
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


async def get_user_by_id(user_id: int, session: Connection) -> users_schema.User:
    query = '''SELECT * FROM users WHERE id = :id'''
    result = await session.fetch_one(query=query, values={'id': user_id})
    return users_schema.User.from_orm(result) if result else None


async def get_no_password_user_by_id(user_id: int, session: Connection) -> users_schema.NoPasswordUser:
    query = '''SELECT id, email, login, role, active FROM users;'''
    result = await session.fetch_one(query=query, values={'id': user_id})
    return users_schema.NoPasswordUser.from_orm(result) if result else None


async def get_user_by_login(login: str, session: Connection) -> users_schema.User:
    query = '''SELECT * FROM users WHERE login = :login;'''
    result = await session.fetch_one(query=query, values={'login': login})
    return users_schema.User.from_orm(result) if result else None


async def get_users(session: Connection) -> list[users_schema.NoPasswordUser]:
    query = '''SELECT id, email, login, role, active FROM users;'''
    result = await session.fetch_all(query=query)
    users = [users_schema.NoPasswordUser.from_orm(user_data) for user_data in result]
    return users


async def insert_user(user_data: users_schema.NewUserData, session: Connection):
    query = '''INSERT INTO users(email, login, password_hash, role) VALUES 
    (:email, :login, :password, :role);'''
    values = user_data.dict()
    await session.execute(query=query, values=values)


async def update_user(user_data: users_schema.User, session: Connection):
    query = '''UPDATE users SET email = :email, login = :login, password_hash = :password_hash,
    active = :active, role = :role WHERE id = :id;'''
    values = user_data.dict()
    await session.execute(query=query, values=values)


async def delete_user(user_id: int, session: Connection):
    query = '''DELETE FROM users WHERE id = :id'''
    await session.execute(query, {'id': user_id})


async def get_book_by_id(book_id: int, session: Connection) -> books_schema.Book:
    query = '''SELECT * FROM books WHERE id = :id'''
    result = await session.fetch_one(query=query, values={'id': book_id})
    return books_schema.Book.from_orm(result) if result else None


async def get_book_by_name(book_name: str, session: Connection) -> books_schema.Book:
    query = '''SELECT * FROM books WHERE name = :name'''
    result = await session.fetch_one(query=query, values={'name': book_name})
    return books_schema.Book.from_orm(result) if result else None


async def search_books(session: Connection, filter_name: str = None,
                       filter_value: int = None) -> list[books_schema.Book]:
    if filter_name and filter_value:
        query = '''SELECT * FROM books WHERE :filter_name = :value;'''
        result = await session.fetch_all(query=query, values={'value': filter_value, 'filter_name': filter_name})
    else:
        query = '''SELECT * FROM books;'''
        result = await session.fetch_all(query=query)
    result = [books_schema.Book.from_orm(item) for item in result]
    return result


async def insert_book(book_data: books_schema.NewBookData, session: Connection):
    query = '''INSERT INTO books(name, author_id, publisher_id, genre_id) 
    VALUES(:name, :author_id, :publisher_id, :genre_id);'''
    values = dict(book_data)
    del values['author'], values['publisher'], values['genre']
    await session.execute(query=query, values=values)


async def update_book(book_data: books_schema.Book, session: Connection):
    query = '''UPDATE books SET name = :name, author_id = :author_id, publisher_id = :publisher_id,
    genre_id = :genre_id, reserved_datetime = :reserved_datetime, reserver_id = :reserved_user_id,
    in_stock = :in_stock, owner_id = :owner_id WHERE id = :id;'''
    values = book_data.dict()
    await session.execute(query=query, values=values)


async def delete_book(book_id: int, session: Connection):
    query = f'''DELETE FROM books WHERE id = :id'''
    await session.execute(query=query, values={'id': book_id})


async def get_genre_by_id(genre_id: int, session: Connection) -> misc_schema.Genre:
    query = '''SELECT * FROM genres WHERE id = :id;'''
    result = await session.fetch_one(query=query, values={'id': genre_id})
    return misc_schema.Genre.from_orm(result) if result else None


async def get_or_insert_genre(genre_name: str, session: Connection) -> misc_schema.Genre:
    query = '''SELECT * FROM genres WHERE name = :name;'''
    result = await session.fetch_one(query, values={'name': genre_name})
    if not result:
        query = '''INSERT INTO genres (name) VALUES (:name) RETURNING *;'''
        result = await session.fetch_one(query=query, values={'name': genre_name})
    return misc_schema.Genre.from_orm(result)


async def get_author_by_id(author_id: int, session: Connection) -> misc_schema.Author:
    query = '''SELECT * FROM authors WHERE id = :id;'''
    result = await session.fetch_one(query=query, values={'id': author_id})
    return misc_schema.Author.from_orm(result) if result else None


async def get_or_insert_author(author_name: str, session: Connection) -> misc_schema.Author:
    query = '''SELECT * FROM authors WHERE name = :name;'''
    result = await session.fetch_one(query, values={'name': author_name})
    if not result:
        query = '''INSERT INTO authors (name) VALUES (:name) RETURNING *;'''
        result = await session.fetch_one(query=query, values={'name': author_name})
    return misc_schema.Author.from_orm(result)


async def get_publisher_by_id(publisher_id: int, session: Connection) -> misc_schema.Publisher:
    query = '''SELECT * FROM publishers WHERE id = :id;'''
    result = await session.fetch_one(query=query, values={'id': publisher_id})
    return misc_schema.Publisher.from_orm(result) if result else None


async def get_or_insert_publisher(publisher_name: str, session: Connection) -> misc_schema.Publisher:
    query = '''SELECT * FROM publishers WHERE name = :name;'''
    result = await session.fetch_one(query, values={'name': publisher_name})
    if not result:
        query = '''INSERT INTO publishers (name) VALUES (:name) RETURNING *;'''
        result = await session.fetch_one(query=query, values={'name': publisher_name})
    return misc_schema.Publisher.from_orm(result)