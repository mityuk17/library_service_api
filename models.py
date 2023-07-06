import time
from dataclasses import dataclass
import settings


@dataclass
class Genre:
    id: int
    name: str


@dataclass
class Author:
    id: int
    name: str


@dataclass
class Publisher:
    id: int
    name: str


@dataclass
class Book:
    id: int
    name: str
    author: str
    publisher: str
    genre_id: int
    reserved_datetime: int
    reserved_user_id: int
    in_stock: bool
    owner_id: int

    def to_data_dict(self):
        return {'id': self.id,
                'name': self.name,
                'author': self.author,
                'publisher': self.publisher,
                'genre_id': self.genre_id,
                'reserved_datetime': self.reserved_datetime,
                'reserved_user_id': self.reserved_user_id,
                'in_stock': self.in_stock,
                'owner_id': self.owner_id}

    def is_reserved(self):
        return self.reserved_datetime + settings.reservation_time > time.time()


@dataclass
class User:
    id: int
    email: str
    login: str
    password: str
    role: str
    active: bool

    def to_data_dict(self):
        return {'id': self.id,
                'email': self.email,
                'login': self.login,
                'password': self.password,
                'role': self.role,
                'active': self.active}

    def validate_password(self, password):
        return self.password == password
