import time
from pydantic import BaseModel
import settings

"""
Classes for Book class params
"""


class Genre(BaseModel):
    id: int
    name: str

    @classmethod
    def from_list(cls, list_data: list):
        return Genre(id=list_data[0], name=list_data[1])


class Author(BaseModel):
    id: int
    name: str

    @classmethod
    def from_list(cls, list_data: list):
        return Author(id=list_data[0], name=list_data[1])


class Publisher(BaseModel):
    id: int
    name: str

    @classmethod
    def from_list(cls, list_data: list):
        return Publisher(id=list_data[0], name=list_data[1])


class Authorization(BaseModel):
    login: str
    password: str


class UpdatedUserData(BaseModel):
    authorization: Authorization
    id: int
    email: str = None
    login: str = None
    password: str = None
    role: str = None
    active: bool = None


class UpdatedBookData(BaseModel):
    authorization: Authorization
    id: int
    name: str = None
    author_id: int = None
    publisher_id: int = None
    genre_id: int = None
    reserved_datetime: int = None
    reserved_user_id: int = None
    in_stock: bool = None
    owner_id: int = None


class Book(BaseModel):
    id: int
    name: str
    author_id: int
    publisher_id: int
    genre_id: int
    reserved_datetime: int
    reserved_user_id: int
    in_stock: bool
    owner_id: int

    @classmethod
    def from_list(cls, book_data: list):
        book = Book(id=book_data[0], name=book_data[1], author_id=book_data[2], publisher_id=book_data[3],
                    genre_id=book_data[4], reserved_datetime=book_data[4], in_stock=book_data[5], owner_id=book_data[6])
        return book

    @classmethod
    def from_dict(cls, book_data: dict):
        book_id = book_data.get('id')
        name = book_data.get('name')
        author_id = book_data.get('author_id')
        publisher_id = book_data.get('publisher_id')
        genre_id = book_data.get('genre_id')
        reserved_datetime = book_data.get('reserved_datetime')
        reserved_user_id = book_data.get('reserved_user_id')
        in_stock = book_data.get('in_stock')
        owner_id = book_data.get('owner_id')
        return Book(id=book_id, name=name, author_id=author_id, publisher_id=publisher_id, genre_id=genre_id,
                    reserved_datetime=reserved_datetime, reserved_user_id=reserved_user_id, in_stock=in_stock,
                    owner_id=owner_id)

    def is_reserved(self):
        return self.reserved_datetime + settings.reservation_time > time.time()


class User(BaseModel):
    id: int
    email: str
    login: str
    password: str
    role: str
    active: bool

    @classmethod
    def from_list(cls, user_data: list):
        user = cls(id=user_data[0], email=user_data[1], login=user_data[2], password=user_data[3],
                   role=user_data[4], active=user_data[5])
        return user

    @classmethod
    def from_dict(cls, user_data: dict):
        user_id = user_data.get('id')
        email = user_data.get('email')
        login = user_data.get('login')
        password = user_data.get('password')
        role = user_data.get('role')
        active = user_data.get('active')
        return cls(id=user_id, email=email, login=login, password=password, role=role, active=active)


class NewUserData(BaseModel):
    authorization: Authorization
    email: str
    login: str
    password: str
    role: str


class NewBookData(BaseModel):
    authorization: Authorization
    name: str
    author: str
    publisher: str
    genre: str
    author_id: int = None
    publisher_id: int = None
    genre_id: int = None


class BookGiveTransaction(BaseModel):
    authorization: Authorization
    user_id: int
    book_id: int


class BookGetTransaction(BaseModel):
    authorization: Authorization
    book_id: int


class GenericResponse(BaseModel):
    result: bool
