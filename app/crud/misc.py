from typing import AsyncGenerator, Any, Union
from databases.core import Connection, Database
from app.settings import postgre_url
import databases.backends.postgres
from passlib.hash import bcrypt
from app.schemas import miscs, users
from app.crud.user import get_user_by_login


databases.backends.postgres.Record.__iter__ = lambda self: iter(self._row)


async def get_session() -> AsyncGenerator[Connection, Any]:
    """Return DB session"""
    async with Database(postgre_url) as db, db.connection() as conn:
        yield conn


async def authorize(authorization: miscs.Authorization,
                    required_role: str, session: Connection) -> Union[users.User, None]:
    """
    Checks equivalence of given password hash and hash from database
    :param session: DB connection session
    :param authorization: login and password
    :param required_role:
    :return: schemas.User
    """
    user = await get_user_by_login(login=authorization.login, session=session)
    if not user or user.role != required_role:
        return
    check = bcrypt.verify(secret=authorization.password, hash=user.password_hash)
    return user if check else None


async def get_genre_by_id(genre_id: int, session: Connection) -> miscs.Genre:
    query = '''SELECT * FROM genres WHERE id = :id;'''
    result = await session.fetch_one(query=query, values={'id': genre_id})
    return miscs.Genre.from_orm(result) if result else None


async def get_or_insert_genre(genre_name: str, session: Connection) -> miscs.Genre:
    query = '''SELECT * FROM genres WHERE name = :name;'''
    result = await session.fetch_one(query, values={'name': genre_name})
    if not result:
        query = '''INSERT INTO genres (name) VALUES (:name) RETURNING *;'''
        result = await session.fetch_one(query=query, values={'name': genre_name})
    return miscs.Genre.from_orm(result)


async def get_author_by_id(author_id: int, session: Connection) -> miscs.Author:
    query = '''SELECT * FROM authors WHERE id = :id;'''
    result = await session.fetch_one(query=query, values={'id': author_id})
    return miscs.Author.from_orm(result) if result else None


async def get_or_insert_author(author_name: str, session: Connection) -> miscs.Author:
    query = '''SELECT * FROM authors WHERE name = :name;'''
    result = await session.fetch_one(query, values={'name': author_name})
    if not result:
        query = '''INSERT INTO authors (name) VALUES (:name) RETURNING *;'''
        result = await session.fetch_one(query=query, values={'name': author_name})
    return miscs.Author.from_orm(result)


async def get_publisher_by_id(publisher_id: int, session: Connection) -> miscs.Publisher:
    query = '''SELECT * FROM publishers WHERE id = :id;'''
    result = await session.fetch_one(query=query, values={'id': publisher_id})
    return miscs.Publisher.from_orm(result) if result else None


async def get_or_insert_publisher(publisher_name: str, session: Connection) -> miscs.Publisher:
    query = '''SELECT * FROM publishers WHERE name = :name;'''
    result = await session.fetch_one(query, values={'name': publisher_name})
    if not result:
        query = '''INSERT INTO publishers (name) VALUES (:name) RETURNING *;'''
        result = await session.fetch_one(query=query, values={'name': publisher_name})
    return miscs.Publisher.from_orm(result)
