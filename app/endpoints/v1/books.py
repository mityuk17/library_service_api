from databases.core import Connection
from fastapi import APIRouter, Depends, HTTPException
from app.crud import book as db_book
from app.crud import misc as db_misc
from app.schemas import books

router = APIRouter(prefix="/api/v1/books")


@router.get('/', response_model=list[books.Book])
async def get_books(session: Connection = Depends(db_misc.get_session)):
    """
    Gives all books
    :return: list[schemas.Book]
    """
    all_books = await db_book.search_books(session)
    return all_books


@router.get('/{book_id}', response_model=books.Book)
async def get_book(book_id: int, session: Connection = Depends(db_misc.get_session)):
    """
    Get book by its id
    :param session: Connection object
    :param book_id:
    :return: schemas.Book
    """
    book = await db_book.get_book_by_id(book_id, session)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    return book


@router.get('/genre/{genre_id}', response_model=list[books.Book])
async def search_books_by_genre(genre_id: int, session: Connection = Depends(db_misc.get_session)):
    """
    Gets books specified by genre
    :param session: Connection object
    :param genre_id:
    :return: list of Book objects
    """
    genre = await db_misc.get_genre_by_id(genre_id, session)
    if not genre:
        return HTTPException(status_code=404, detail='Genre not found')
    all_books = await db_book.search_books(filter_name='genre_id', filter_value=genre.id, session=session)
    return all_books


@router.get('/publisher/{publisher_id}', response_model=list[books.Book])
async def search_books_by_publisher(publisher_id: int, session: Connection = Depends(db_misc.get_session)):
    """
    Gets books specified by publisher
    :param session: Connection object
    :param publisher_id:
    :return: list of Book objects
    """
    publisher = await db_misc.get_publisher_by_id(publisher_id, session)
    if not publisher:
        return HTTPException(status_code=404, detail='Publisher not found')
    all_books = await db_book.search_books(filter_name='publisher_id', filter_value=publisher.id, session=session)
    return all_books


@router.get('/author/{author_id}', response_model=list[books.Book])
async def search_books_by_author(author_id: int, session: Connection = Depends(db_misc.get_session)):
    """
    Gets books specified by author
    :param session: Connection object
    :param author_id:
    :return: list of Book objects
    """
    author = await db_misc.get_author_by_id(author_id, session)
    if not author:
        return HTTPException(status_code=404, detail='Publisher not found')
    all_books = await db_book.search_books(filter_name='author_id', filter_value=author.id, session=session)
    return all_books
