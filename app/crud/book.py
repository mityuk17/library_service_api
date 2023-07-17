from databases.core import Connection
import databases.backends.postgres
from app.schemas import books


databases.backends.postgres.Record.__iter__ = lambda self: iter(self._row)


async def get_book_by_id(book_id: int, session: Connection) -> books.Book:
    query = '''SELECT * FROM books WHERE id = :id'''
    result = await session.fetch_one(query=query, values={'id': book_id})
    return books.Book.from_orm(result) if result else None


async def get_book_by_name(book_name: str, session: Connection) -> books.Book:
    query = '''SELECT * FROM books WHERE name = :name'''
    result = await session.fetch_one(query=query, values={'name': book_name})
    return books.Book.from_orm(result) if result else None


async def search_books(session: Connection, filter_name: str = None,
                       filter_value: int = None) -> list[books.Book]:
    if filter_name and filter_value:
        query = '''SELECT * FROM books WHERE :filter_name = :value;'''
        result = await session.fetch_all(query=query, values={'value': filter_value, 'filter_name': filter_name})
    else:
        query = '''SELECT * FROM books;'''
        result = await session.fetch_all(query=query)
    result = [books.Book.from_orm(item) for item in result]
    return result


async def insert_book(book_data: books.NewBookData, session: Connection):
    query = '''INSERT INTO books(name, author_id, publisher_id, genre_id) 
    VALUES(:name, :author_id, :publisher_id, :genre_id);'''
    values = book_data.dict(exclude={'author': True, 'publisher': True, 'genre': True})
    await session.execute(query=query, values=values)


async def update_book(book_data: books.Book, session: Connection):
    query = '''UPDATE books SET name = :name, author_id = :author_id, publisher_id = :publisher_id,
    genre_id = :genre_id, reserved_datetime = :reserved_datetime, reserver_id = :reserved_user_id,
    in_stock = :in_stock, owner_id = :owner_id WHERE id = :id;'''
    values = book_data.dict()
    await session.execute(query=query, values=values)


async def delete_book(book_id: int, session: Connection):
    query = f'''DELETE FROM books WHERE id = :id'''
    await session.execute(query=query, values={'id': book_id})
