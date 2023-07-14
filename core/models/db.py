from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Sequence, Boolean, null
from sqlalchemy.orm import declarative_base
from settings import postgre_url


engine = create_engine(postgre_url)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence("users_id_seq", start=1), primary_key=True)
    email = Column(String(50))
    login = Column(String(50), unique=True)
    password_hash = Column(String(150))
    role = Column(String(50))
    active = Column(Boolean, default=True)


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, Sequence("books_id_seq", start=1), primary_key=True)
    name = Column(String(100), unique=True)
    author_id = Column(Integer)
    publisher_id = Column(Integer)
    genre_id = Column(Integer)
    reserved_datatime = Column(Integer, default=0)
    reserver_id = Column(Integer, nullable=True)
    in_stock = Column(Boolean, default=True)
    owner_id = Column(Integer, nullable=True, default=None)


class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, Sequence("genres_id_seq", start=1), primary_key=True)
    name = Column(String(50))


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, Sequence("authors_id_seq", start=1), primary_key=True)
    name = Column(String(100))


class Publisher(Base):
    __tablename__ = 'publishers'
    id = Column(Integer, Sequence("publishers_id_seq", start=1), primary_key=True)
    name = Column(String(100))
