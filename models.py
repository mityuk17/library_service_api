import time

from pydantic import BaseModel

import settings

"""
Classes for Book class params
"""


class Genre(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Author(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Publisher(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Authorization(BaseModel):
    login: str
    password: str


class UpdatedUserData(BaseModel):
    id: int
    email: str = None
    login: str = None
    password: str = None
    role: str = None
    active: bool = None


class UpdatedBookData(BaseModel):
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

    class Config:
        orm_mode = True

    def is_reserved(self):
        return self.reserved_datetime + settings.reservation_time > time.time()


class User(BaseModel):
    id: int
    email: str
    login: str
    password_hash: str
    role: str
    active: bool

    class Config:
        orm_mode = True


class NewUserData(BaseModel):
    email: str
    login: str
    password: str
    role: str


class NewBookData(BaseModel):
    name: str
    author: str
    publisher: str
    genre: str
    author_id: int = None
    publisher_id: int = None
    genre_id: int = None


class BookGiveTransaction(BaseModel):
    user_id: int
    book_id: int


class BookGetTransaction(BaseModel):
    book_id: int


class GenericResponse(BaseModel):
    result: bool


class Token(BaseModel):
    access_token: str
    token_type: str
