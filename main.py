import smtplib
import time
from fastapi import FastAPI, HTTPException
import db
import models
import settings
import utils

app = FastAPI()
email_controller = smtplib.SMTP()


@app.on_event('startup')
async def startup():
    await db.database.connect()
    await db.create_tables()
    email_controller.connect(settings.EMAIL_DOMEN_NAME, settings.EMAIL_PORT)
    email_controller.starttls()
    email_controller.login(settings.EMAIL_LOGIN, settings.EMAIL_PASSWORD)


@app.on_event('shutdown')
async def shutdown():
    await db.database.disconnect()
    email_controller.quit()


@app.get("/")
async def root():
    return {"status": "OK"}


"""
Admin methods
"""


@app.get('/api/admin/users', response_model=list[models.User])
async def get_users(authorization: models.Authorization):
    """
    Get information about all users
    :param authorization: login, password
    :return: users list[User]
    """
    authorized_user = await db.authorize(authorization, 'admin')
    if not authorized_user:
        return HTTPException(status_code=401)
    users = await db.get_users()
    return users


@app.post('/api/admin/users', response_model=models.GenericResponse)
async def create_user(new_user: models.NewUserData):
    """
    Creates a new user
    :param new_user: admin_authorization(models.Authorization) and new user data
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(new_user.authorization, 'admin')
    if not authorized_user:
        return HTTPException(status_code=401)
    await db.insert_user(new_user)
    utils.notify_about_account_creation(email_controller, new_user)
    return models.GenericResponse(result=True)


@app.put('/api/admin/users', response_model=models.GenericResponse)
async def change_user_data(updated_user_data: models.UpdatedUserData):
    """
    Updates User's fields' values
    :param updated_user_data: authorization(models.Authorization) and updated user data
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(updated_user_data.authorization, 'admin')
    if not authorized_user:
        return HTTPException(status_code=401)
    user = await db.get_user_by_id(updated_user_data.id)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    updated_user = models.User(**(user.dict() | updated_user_data.dict()))
    await db.update_user(updated_user)
    return models.GenericResponse(result=True)


@app.get('/api/admin/users/{user_id}', response_model=models.User)
async def get_user_info(user_id: int, authorization: models.Authorization):
    """
    Gets user information by id
    :param user_id:
    :param authorization: login and password
    :return: models.User
    """
    authorized_user = await db.authorize(authorization, 'admin')
    if not authorized_user:
        return HTTPException(status_code=401)
    user = await db.get_user_by_id(user_id)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    return user


@app.delete('/api/admin/users/{user_id}', response_model=models.GenericResponse)
async def delete_user(user_id: int, authorization: models.Authorization):
    """
    Deletes user from database
    :param user_id:
    :param authorization: login and password
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(authorization, 'admin')
    if not authorized_user:
        return HTTPException(status_code=401)
    await db.delete_user(user_id)
    return models.GenericResponse(result=True)


"""
Librarian methods
"""


@app.post('/api/librarian/books', response_model=models.GenericResponse)
async def create_book(new_book: models.NewBookData):
    """
    Creates new book
    :param new_book: authorization and new book data
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(new_book.authorization, 'librarian')
    if not authorized_user:
        return HTTPException(status_code=401)
    author = await db.get_or_insert_author(author_name=new_book.author)
    genre = await db.get_or_insert_genre(genre_name=new_book.genre)
    publisher = await db.get_or_insert_publisher(publisher_name=new_book.publisher)
    new_book.author_id = author.id
    new_book.genre_id = genre.id
    new_book.publisher_id = publisher.id
    await db.insert_book(new_book)
    return models.GenericResponse(result=True)


@app.put('/api/librarian/books', response_model=models.GenericResponse)
async def change_book_data(updated_book_data: models.UpdatedBookData):
    """
    Changes Book object's fields' values
    :param updated_book_data: authorization and updated book data
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(updated_book_data.authorization, 'librarian')
    if not authorized_user:
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(updated_book_data.id)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    updated_book = models.Book(**(book.dict() | updated_book_data.dict()))
    await db.update_book(updated_book)
    return models.GenericResponse(result=True)


@app.get('/api/librarian/books/{book_id}', response_model=models.Book)
async def get_book_info(book_id: int, authorization: models.Authorization):
    """
    Get book by id
    :param book_id:
    :param authorization: login and password
    :return: models.Book
    """
    authorized_user = await db.authorize(authorization, 'librarian')
    if not authorized_user:
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(book_id=book_id)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    return book


@app.delete('/api/librarian/books/{book_id}', response_model=models.GenericResponse)
async def delete_book(book_id: int, authorization: models.Authorization):
    """
    Delete book from database
    :param book_id:
    :param authorization: login and password
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(authorization, 'librarian')
    if not authorized_user:
        return HTTPException(status_code=401)
    await db.delete_book(book_id)
    return models.GenericResponse(result=True)


@app.get('/api/librarian/give_book', response_model=models.GenericResponse)
async def give_book(book_transaction: models.BookGiveTransaction):
    """
    Makes book unavailable for reserving of taking by users
    :param book_transaction: authorization, book_id, user_id
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(book_transaction.authorization, 'librarian')
    if not authorized_user:
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(book_transaction.book_id)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    user = await db.get_user_by_id(book_transaction.user_id)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    if book.is_reserved() and book.reserved_user_id != user.id:
        return HTTPException(status_code=403, detail='Book is reserved by other user')
    if not book.in_stock:
        return HTTPException(status_code=403, detail='Book is not in stock')
    book.in_stock = False
    book.owner_id = user.id
    await db.update_book(book_data=book)
    return models.GenericResponse(result=True)


@app.get('/api/librarian/take_book', response_model=models.GenericResponse)
async def take_book(book_transaction: models.BookGetTransaction):
    """
    Makes book available for reserving and taking by users
    :param book_transaction: authorization, book_id)
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(book_transaction.authorization, 'librarian')
    if not authorized_user:
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(book_transaction.book_id)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    if book.in_stock:
        return HTTPException(status_code=403, detail='Book is already in stock')
    book.in_stock = True
    await db.update_book(book)
    return models.GenericResponse(result=True)


"""
User methods
"""


@app.get('/api/reserve_book/{book_id}', response_model=models.GenericResponse)
async def reserve_book(book_id: int, authorization: models.Authorization):
    """
    Reserves book and make it unavailable to reserve or take it by other users
    :param book_id:
    :param authorization: login and password
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(authorization, 'user')
    if not authorized_user:
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(book_id=book_id)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    if book.is_reserved():
        return HTTPException(status_code=403, detail='Book is already reserved')
    if not book.in_stock:
        return HTTPException(status_code=403, detail='Book is not in stock')
    book.reserved_datetime = int(time.time())
    book.reserved_user_id = authorized_user.id
    await db.update_book(book)
    return models.GenericResponse


@app.get('/api/unreserve_book/{book_id}', response_model=models.GenericResponse)
async def unreserve_book(book_id: int, authorization: models.Authorization):
    """
    Unreserve a book if it is reserved by user
    :param book_id:
    :param authorization:
    :return: models.GenericResponse
    """
    authorized_user = await db.authorize(authorization, 'user')
    if not authorized_user:
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(book_id)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    if not book.is_reserved():
        return HTTPException(status_code=403, detail='Book is not reserved')
    if book.is_reserved() and book.reserved_user_id != authorized_user.id:
        return HTTPException(status_code=403, detail='Book is reserved by another user')
    book.reserved_datetime = 0
    await db.update_book(book)
    return models.GenericResponse(result=True)

"""
Methods without authorization
"""


@app.get('/api/books', response_model=list[models.Book])
async def get_books():
    """
    Gives all books
    :return: list[models.Book]
    """
    books = await db.search_books()
    return books


@app.get('/api/books/{book_id}', response_model=models.Book)
async def get_book(book_id: int):
    """
    Get book by its id
    :param book_id:
    :return: models.Book
    """
    book = await db.get_book_by_id(book_id=book_id)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    return book


@app.get('/api/books/genre/{genre_id}', response_model=list[models.Book])
async def search_books_by_genre(genre_id: int):
    """
    Gets books specified by genre
    :param genre_id:
    :return: list of Book objects
    """
    genre = await db.get_genre_by_id(genre_id=genre_id)
    if not genre:
        return HTTPException(status_code=404, detail='Genre not found')
    books = await db.search_books(filter_name='genre_id', filter_value=genre.id)
    return books


@app.get('/api/books/publisher/{publisher_id}', response_model=list[models.Book])
async def search_books_by_publisher(publisher_id: int):
    """
    Gets books specified by publisher
    :param publisher_id:
    :return: list of Book objects
    """
    publisher = await db.get_publisher_by_id(publisher_id=publisher_id)
    if not publisher:
        return HTTPException(status_code=404, detail='Publisher not found')
    books = await db.search_books(filter_name='publisher_id', filter_value=publisher.id)
    return books


@app.get('/api/books/author/{author_id}', response_model=list[models.Book])
async def search_books_by_author(author_id: int):
    """
    Gets books specified by author
    :param author_id:
    :return: list of Book objects
    """
    author = await db.get_author_by_id(author_id=author_id)
    if not author:
        return HTTPException(status_code=404, detail='Publisher not found')
    books = await db.search_books(filter_name='author_id', filter_value=author.id)
    return books
