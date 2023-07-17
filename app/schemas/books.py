from pydantic import BaseModel
from time import time
from app import settings


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
    reserved_user_id: int = None
    in_stock: bool
    owner_id: int = None

    class Config:
        orm_mode = True

    def is_reserved(self):
        return self.reserved_datetime + settings.reservation_time > time()


class NewBookData(BaseModel):
    name: str
    author: str
    publisher: str
    genre: str
    author_id: int = None
    publisher_id: int = None
    genre_id: int = None
