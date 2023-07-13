import sys
import time
from databases.core import Connection
from asyncpg import PostgresError
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import db
import models
import settings
import utils

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


async def get_current_user(token: str = Depends(oauth2_scheme), session: Connection = Depends(db.get_session)):
    """
    :param token: JWT
    :param session: Connection object
    :return: models.User object
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        login = payload.get("sub")
        if login is None:
            return
    except jwt.exceptions.PyJWTError:
        return
    user = await db.get_user_by_login(login, session)
    if user is None:
        return
    return user


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


@app.get('/api/admin/users', response_model=list[models.NoPasswordUser])
async def get_users(authorized_user: models.User = Depends(get_current_user),
                    session: Connection = Depends(db.get_session)):
    """
    Get information about all users
    :param authorized_user: models.User
    :param session: Connection object
    :return: users list[models.NoPasswordUser]
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    users = await db.get_users(session)
    return users


@app.post('/api/admin/users', response_model=models.GenericResponse)
async def create_user(new_user: models.NewUserData, background_tasks: BackgroundTasks,
                      authorized_user: models.User = Depends(get_current_user),
                      session: Connection = Depends(db.get_session)):
    """
    Creates a new user
    :param session: Connection object
    :param background_tasks: Background tasks
    :param new_user: new user data
    :param authorized_user: models.User object
    :return: models.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    new_user.password = utils.get_password_hash(new_user.password)
    await db.insert_user(new_user, session)
    background_tasks.add_task(utils.notify_about_account_creation, new_user)
    return models.GenericResponse(result=True)


@app.put('/api/admin/users', response_model=models.GenericResponse)
async def change_user_data(updated_user_data: models.UpdatedUserData,
                           authorized_user: models.User = Depends(get_current_user),
                           session: Connection = Depends(db.get_session)):
    """
    Updates User's fields' values
    :param session: Connection object
    :param updated_user_data: updated user data
    :param authorized_user: models.User object
    :return: models.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    user = await db.get_user_by_id(updated_user_data.id, session)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    if updated_user_data.password:
        updated_user_data.password = utils.get_password_hash(updated_user_data.password)
    updated_user = models.User(**(utils.unite_dicts(user.dict(), updated_user_data.dict())))
    await db.update_user(updated_user, session)
    return models.GenericResponse(result=True)


@app.get('/api/admin/users/{user_id}', response_model=models.NoPasswordUser)
async def get_user_info(user_id: int, authorized_user: models.User = Depends(get_current_user),
                        session: Connection = Depends(db.get_session)):
    """
    Gets user information by id
    :param session: Connection object
    :param user_id:
    :param authorized_user: models.User object
    :return: models.NoPasswordUser
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    user = await db.get_no_password_user_by_id(user_id, session)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    return user


@app.delete('/api/admin/users/{user_id}', response_model=models.GenericResponse)
async def delete_user(user_id: int, authorized_user: models.User = Depends(get_current_user),
                      session: Connection = Depends(db.get_session)):
    """
    Deletes user from database
    :param session: Connection object
    :param user_id:
    :param authorized_user: models.User object
    :return: models.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    await db.delete_user(user_id, session)
    return models.GenericResponse(result=True)


"""
Librarian methods
"""


@app.post('/api/librarian/books', response_model=models.GenericResponse)
async def create_book(new_book: models.NewBookData, authorized_user: models.User = Depends(get_current_user),
                      session: Connection = Depends(db.get_session)):
    """
    Creates new book
    :param session: Connection object
    :param new_book: new book data
    :param authorized_user: models.User object
    :return: models.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('librarian')):
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
async def change_book_data(updated_book_data: models.UpdatedBookData,
                           authorized_user: models.User = Depends(get_current_user),
                           session: Connection = Depends(db.get_session)):
    """
    Changes Book object's fields' values
    :param session: Connection object
    :param updated_book_data: updated book data
    :param authorized_user: models.User object
    :return: models.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('librarian')):
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(updated_book_data.id, session)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    updated_book = models.Book(**(utils.unite_dicts(book.dict(), updated_book_data.dict())))
    await db.update_book(updated_book, session)
    return models.GenericResponse(result=True)


@app.get('/api/librarian/books/{book_id}', response_model=models.Book)
async def get_book_info(book_id: int, authorized_user: models.User = Depends(get_current_user),
                        session: Connection = Depends(db.get_session)):
    """
    Get book by id
    :param session: Connection object
    :param book_id:
    :param authorized_user: models.User object
    :return: models.Book
    """
    if not (authorized_user and authorized_user.check_role('librarian')):
        return HTTPException(status_code=401)
    book = await db.get_book_by_id(book_id, session)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    return book


@app.delete('/api/librarian/books/{book_id}', response_model=models.GenericResponse)
async def delete_book(book_id: int, authorized_user: models.User = Depends(get_current_user),
                      session: Connection = Depends(db.get_session)):
    """
    Delete book from database
    :param session: Connection object
    :param book_id:
    :param authorized_user: models.User object
    :return: models.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('librarian')):
        return HTTPException(status_code=401)
    await db.delete_book(book_id, session)
    return models.GenericResponse(result=True)


@app.get('/api/librarian/give_book', response_model=models.GenericResponse)
async def give_book(book_transaction: models.BookGiveTransaction,
                    authorized_user: models.User = Depends(get_current_user),
                    session: Connection = Depends(db.get_session)):
    """
    Makes book unavailable for reserving of taking by users
    :param session: Connection object
    :param book_transaction: book_id, user_id
    :param authorized_user: models.User object
    :return: models.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('librarian')):
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
async def take_book(book_transaction: models.BookGetTransaction,
                    authorized_user: models.User = Depends(get_current_user),
                    session: Connection = Depends(db.get_session)):
    """
    Makes book available for reserving and taking by users
    :param session: Connection object
    :param book_transaction: book_id
    :param authorized_user: models.User object
    :return: models.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('librarian')):
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
async def reserve_book(book_id: int, authorized_user: models.User = Depends(get_current_user),
                       session: Connection = Depends(db.get_session)):
    """
    Reserves book and make it unavailable to reserve or take it by other users
    :param session: Connection object
    :param book_id:
    :param authorized_user: models.User object
    :return: models.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('user')):
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
async def unreserve_book(book_id: int, authorized_user: models.User = Depends(get_current_user),
                         session: Connection = Depends(db.get_session)):
    """
    Unreserves a book if it is reserved by user
    :param session: Connection object
    :param book_id:
    :param authorized_user: models.User object
    :return: models.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('user')):
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


@app.post("/token", response_model=models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 session: Connection = Depends(db.get_session)):
    user = await utils.authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=401)
    access_token = utils.create_access_token(
        data={"sub": user.login}
    )
    return models.Token(access_token=access_token, token_type='bearer')
