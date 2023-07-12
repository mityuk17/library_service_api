import sys
import time
from databases.core import Connection
from asyncpg import PostgresError
from fastapi import FastAPI, HTTPException, Depends
import db
import models
import utils


app = FastAPI()


@app.on_event('startup')
async def startup():
    try:
        async for session in db.get_session():
            check = await session.fetch_one("SELECT 1;")
            await db.create_tables(session)
            print(check)
    except PostgresError:
        print("DB connection error")
        sys.exit(1)


"""
Admin methods
"""


@app.get('/api/admin/users', response_model=list[models.User])
async def get_users(authorization: models.Authorization, session: Connection = Depends(db.get_session)):
    """
    Get information about all users
    :param session: Connection object
    :param authorization: login, password
    :return: users list[User]
    """
    authorized_user = await db.authorize(authorization, 'admin', session)
    if not authorized_user:
        return HTTPException(status_code=401)
    users = await db.get_users(session)
    return users


@app.post('/api/admin/users', response_model=models.GenericResponse)
async def create_user(new_user: models.NewUserData, session: Connection = Depends(db.get_session)):
    """
    Creates a new user
    :param session: Connection object
    :param new_user: admin_authorization(models.Authorization) and new user data
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(new_user.authorization, 'admin', session)
    if not authorized_user:
        return HTTPException(status_code=401)
    await db.insert_user(new_user, session)
    utils.notify_about_account_creation(new_user)
    return models.GenericResponse(result=True)


@app.put('/api/admin/users', response_model=models.GenericResponse)
async def change_user_data(updated_user_data: models.UpdatedUserData, session: Connection = Depends(db.get_session)):
    """
    Updates User's fields' values
    :param session: Connection object
    :param updated_user_data: authorization(models.Authorization) and updated user data
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(updated_user_data.authorization, 'admin', session)
    if not authorized_user:
        return HTTPException(status_code=401)
    user = await db.get_user_by_id(updated_user_data.id, session)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    updated_user = models.User(**(user.dict() | updated_user_data.dict()))
    await db.update_user(updated_user, session)
    return models.GenericResponse(result=True)


@app.get('/api/admin/users/{user_id}', response_model=models.User)
async def get_user_info(user_id: int, authorization: models.Authorization,
                        session: Connection = Depends(db.get_session)):
    """
    Gets user information by id
    :param session: Connection object
    :param user_id:
    :param authorization: login and password
    :return: models.User
    """
    authorized_user = await db.authorize(authorization, 'admin', session)
    if not authorized_user:
        return HTTPException(status_code=401)
    user = await db.get_user_by_id(user_id, session)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    return user


@app.delete('/api/admin/users/{user_id}', response_model=models.GenericResponse)
async def delete_user(user_id: int, authorization: models.Authorization, session: Connection = Depends(db.get_session)):
    """
    Deletes user from database
    :param session: Connection object
    :param user_id:
    :param authorization: login and password
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(authorization, 'admin', session)
    if not authorized_user:
        return HTTPException(status_code=401)
    await db.delete_user(user_id, session)
    return models.GenericResponse(result=True)


"""
Librarian methods
"""


@app.post('/api/librarian/books', response_model=models.GenericResponse)
async def create_book(new_book: models.NewBookData, session: Connection = Depends(db.get_session)):
    """
    Creates new book
    :param session: Connection object
    :param new_book: authorization and new book data
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(new_book.authorization, 'librarian', session)
    if not authorized_user:
        return HTTPException(status_code=401)
    author = await db.get_or_insert_author(new_book.author, session)
    genre = await db.get_or_insert_genre(new_book.genre, session)
    publisher = await db.get_or_insert_publisher(new_book.publisher, session)
    new_book.author_id = author.id
    new_book.genre_id = genre.id
    new_book.publisher_id = publisher.id
    await db.insert_book(new_book, session)
    return models.GenericResponse(result=True)


@app.put('/api/librarian/books', response_model=models.GenericResponse)
async def change_book_data(updated_book_data: models.UpdatedBookData, session: Connection = Depends(db.get_session)):
    """
    Changes Book object's fields' values
    :param session: Connection object
    :param updated_book_data: authorization and updated book data
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(updated_book_data.authorization, 'librarian', session)
    if not authorized_user:
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(updated_book_data.id, session)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    updated_book = models.Book(**(book.dict() | updated_book_data.dict()))
    await db.update_book(updated_book, session)
    return models.GenericResponse(result=True)


@app.get('/api/librarian/books/{book_id}', response_model=models.Book)
async def get_book_info(book_id: int, authorization: models.Authorization,
                        session: Connection = Depends(db.get_session)):
    """
    Get book by id
    :param session: Connection object
    :param book_id:
    :param authorization: login and password
    :return: models.Book
    """
    authorized_user = await db.authorize(authorization, 'librarian', session)
    if not authorized_user:
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(book_id, session)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    return book


@app.delete('/api/librarian/books/{book_id}', response_model=models.GenericResponse)
async def delete_book(book_id: int, authorization: models.Authorization, session: Connection = Depends(db.get_session)):
    """
    Delete book from database
    :param session: Connection object
    :param book_id:
    :param authorization: login and password
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(authorization, 'librarian', session)
    if not authorized_user:
        return HTTPException(status_code=401)
    await db.delete_book(book_id, session)
    return models.GenericResponse(result=True)


@app.get('/api/librarian/give_book', response_model=models.GenericResponse)
async def give_book(book_transaction: models.BookGiveTransaction, session: Connection = Depends(db.get_session)):
    """
    Makes book unavailable for reserving of taking by users
    :param session: Connection object
    :param book_transaction: authorization, book_id, user_id
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(book_transaction.authorization, 'librarian', session)
    if not authorized_user:
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(book_transaction.book_id, session)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    user = await db.get_user_by_id(book_transaction.user_id, session)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    if book.is_reserved() and book.reserved_user_id != user.id:
        return HTTPException(status_code=403, detail='Book is reserved by other user')
    if not book.in_stock:
        return HTTPException(status_code=403, detail='Book is not in stock')
    book.in_stock = False
    book.owner_id = user.id
    await db.update_book(book, session)
    return models.GenericResponse(result=True)


@app.get('/api/librarian/take_book', response_model=models.GenericResponse)
async def take_book(book_transaction: models.BookGetTransaction, session: Connection = Depends(db.get_session)):
    """
    Makes book available for reserving and taking by users
    :param session: Connection object
    :param book_transaction: authorization, book_id)
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(book_transaction.authorization, 'librarian', session)
    if not authorized_user:
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(book_transaction.book_id, session)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    if book.in_stock:
        return HTTPException(status_code=403, detail='Book is already in stock')
    book.in_stock = True
    await db.update_book(book, session)
    return models.GenericResponse(result=True)


"""
User methods
"""


@app.get('/api/reserve_book/{book_id}', response_model=models.GenericResponse)
async def reserve_book(book_id: int, authorization: models.Authorization,
                       session: Connection = Depends(db.get_session)):
    """
    Reserves book and make it unavailable to reserve or take it by other users
    :param session: Connection object
    :param book_id:
    :param authorization: login and password
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(authorization, 'user', session)
    if not authorized_user:
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(book_id, session)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    if book.is_reserved():
        return HTTPException(status_code=403, detail='Book is already reserved')
    if not book.in_stock:
        return HTTPException(status_code=403, detail='Book is not in stock')
    book.reserved_datetime = int(time.time())
    book.reserved_user_id = authorized_user.id
    await db.update_book(book, session)
    return models.GenericResponse


@app.get('/api/unreserve_book/{book_id}', response_model=models.GenericResponse)
async def unreserve_book(book_id: int, authorization: models.Authorization,
                         session: Connection = Depends(db.get_session)):
    """
    Unreserve a book if it is reserved by user
    :param session: Connection object
    :param book_id:
    :param authorization:
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(authorization, 'user', session)
    if not authorized_user:
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(book_id, session)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    if not book.is_reserved():
        return HTTPException(status_code=403, detail='Book is not reserved')
    if book.is_reserved() and book.reserved_user_id != authorized_user.id:
        return HTTPException(status_code=403, detail='Book is reserved by another user')
    book.reserved_datetime = 0
    await db.update_book(book, session)
    return models.GenericResponse(result=True)

"""
Methods without authorization
"""


@app.get('/api/books', response_model=list[models.Book])
async def get_books(session: Connection = Depends(db.get_session)):
    """
    Gives all books
    :return: list[models.Book]
    """
    books = await db.search_books(session)
    return books


@app.get('/api/books/{book_id}', response_model=models.Book)
async def get_book(book_id: int, session: Connection = Depends(db.get_session)):
    """
    Get book by its id
    :param session: Connection object
    :param book_id:
    :return: models.Book
    """
    book = await db.get_book_by_id(book_id, session)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    return book


@app.get('/api/books/genre/{genre_id}', response_model=list[models.Book])
async def search_books_by_genre(genre_id: int, session: Connection = Depends(db.get_session)):
    """
    Gets books specified by genre
    :param session: Connection object
    :param genre_id:
    :return: list of Book objects
    """
    genre = await db.get_genre_by_id(genre_id, session)
    if not genre:
        return HTTPException(status_code=404, detail='Genre not found')
    books = await db.search_books(filter_name='genre_id', filter_value=genre.id, session=session)
    return books


@app.get('/api/books/publisher/{publisher_id}', response_model=list[models.Book])
async def search_books_by_publisher(publisher_id: int, session: Connection = Depends(db.get_session)):
    """
    Gets books specified by publisher
    :param session: Connection object
    :param publisher_id:
    :return: list of Book objects
    """
    publisher = await db.get_publisher_by_id(publisher_id, session)
    if not publisher:
        return HTTPException(status_code=404, detail='Publisher not found')
    books = await db.search_books(filter_name='publisher_id', filter_value=publisher.id, session=session)
    return books


@app.get('/api/books/author/{author_id}', response_model=list[models.Book])
async def search_books_by_author(author_id: int, session: Connection = Depends(db.get_session)):
    """
    Gets books specified by author
    :param session: Connection object
    :param author_id:
    :return: list of Book objects
    """
    author = await db.get_author_by_id(author_id, session)
    if not author:
        return HTTPException(status_code=404, detail='Publisher not found')
    books = await db.search_books(filter_name='author_id', filter_value=author.id, session=session)
    return books
