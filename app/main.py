from asyncpg import PostgresError
from fastapi import FastAPI
from app.endpoints.v1 import admin, user, books, librarian, authorization
from app.crud.misc import get_session
from app.db.models import Base, engine
import sys


app = FastAPI()
app.include_router(admin.router)
app.include_router(librarian.router)
app.include_router(user.router)
app.include_router(books.router)
app.include_router(authorization.router)


@app.on_event('startup')
async def startup():
    Base.metadata.create_all(engine)
    try:
        async for session in get_session():
            check = await session.fetch_one("SELECT 1;")
            print(check)
    except PostgresError:
        print("DB connection error")
        sys.exit(1)