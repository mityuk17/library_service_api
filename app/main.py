from asyncpg import PostgresError
from fastapi import FastAPI
from app.v1 import admin_router, librarian_router, user_router, books_router, authorization_router
import app.core.models.start_database as start_db
import app.core.models.database as db
import sys


app = FastAPI()
app.include_router(admin_router.router)
app.include_router(librarian_router.router)
app.include_router(user_router.router)
app.include_router(books_router.router)
app.include_router(authorization_router.router)


@app.on_event('startup')
async def startup():
    try:
        async for session in db.get_session():
            check = await session.fetch_one("SELECT 1;")
            await start_db.create_tables(session)
            print(check)
    except PostgresError:
        print("DB connection error")
        sys.exit(1)