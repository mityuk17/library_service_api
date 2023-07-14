from databases.core import Connection
from fastapi import APIRouter, Depends, HTTPException
from app.v1 import utils
from app.core.schemas import users_schema
from app.core.schemas import books_schema, misc_schema
import app.core.models.database as db

router = APIRouter(prefix="/api/v1/librarian")


@router.post('/books', response_model=misc_schema.GenericResponse)
async def create_book(new_book: books_schema.NewBookData,
                      authorized_user: users_schema.User = Depends(utils.get_current_user),
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
    return misc_schema.GenericResponse(result=True)


@router.put('/books', response_model=misc_schema.GenericResponse)
async def change_book_data(updated_book_data: books_schema.UpdatedBookData,
                           authorized_user: users_schema.User = Depends(utils.get_current_user),
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
    updated_book = books_schema.Book(**(utils.unite_dicts(book.dict(), updated_book_data.dict())))
    await db.update_book(updated_book, session)
    return misc_schema.GenericResponse(result=True)


@router.get('/books/{book_id}', response_model=books_schema.Book)
async def get_book_info(book_id: int, authorized_user: users_schema.User = Depends(utils.get_current_user),
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


@router.delete('/books/{book_id}', response_model=misc_schema.GenericResponse)
async def delete_book(book_id: int, authorized_user: users_schema.User = Depends(utils.get_current_user),
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
    return misc_schema.GenericResponse(result=True)


@router.get('/give_book', response_model=misc_schema.GenericResponse)
async def give_book(book_transaction: misc_schema.BookGiveTransaction,
                    authorized_user: users_schema.User = Depends(utils.get_current_user),
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
    return misc_schema.GenericResponse(result=True)


@router.get('/take_book', response_model=misc_schema.GenericResponse)
async def take_book(book_transaction: misc_schema.BookGetTransaction,
                    authorized_user: users_schema.User = Depends(utils.get_current_user),
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
    return misc_schema.GenericResponse(result=True)
