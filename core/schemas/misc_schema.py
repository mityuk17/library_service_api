from pydantic import BaseModel


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
