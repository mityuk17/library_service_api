from databases.core import Connection
from fastapi import APIRouter, Depends, HTTPException
from app import utils
from app.crud import book as db_book
from app.crud import misc as db_misc
from app.schemas import users, miscs
from time import time


router = APIRouter(prefix="/api/v1/user")


@router.get('/reserve_book/{book_id}', response_model=miscs.GenericResponse)
async def reserve_book(book_id: int, authorized_user: users.User = Depends(utils.get_current_user),
                       session: Connection = Depends(db_misc.get_session)):
    """
    Reserves book and make it unavailable to reserve or take it by other users
    :param session: Connection object
    :param book_id:
    :param authorized_user: schemas.User object
    :return: schemas.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('user')):
        return HTTPException(status_code=401)
    book = await db_book.get_book_by_id(book_id, session)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    if book.is_reserved():
        return HTTPException(status_code=403, detail='Book is already reserved')
    if not book.in_stock:
        return HTTPException(status_code=403, detail='Book is not in stock')
    book.reserved_datetime = int(time())
    book.reserved_user_id = authorized_user.id
    await db_book.update_book(book, session)
    return miscs.GenericResponse


@router.get('/unreserve_book/{book_id}', response_model=miscs.GenericResponse)
async def unreserve_book(book_id: int, authorized_user: users.User = Depends(utils.get_current_user),
                         session: Connection = Depends(db_misc.get_session)):
    """
    Unreserves a book if it is reserved by user
    :param session: Connection object
    :param book_id:
    :param authorized_user: schemas.User object
    :return: schemas.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('user')):
        return HTTPException(status_code=401)
    book = await db_book.get_book_by_id(book_id, session)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    if not book.is_reserved():
        return HTTPException(status_code=403, detail='Book is not reserved')
    if book.is_reserved() and book.reserved_user_id != authorized_user.id:
        return HTTPException(status_code=403, detail='Book is reserved by another user')
    book.reserved_datetime = 0
    await db_book.update_book(book, session)
    return miscs.GenericResponse(result=True)
