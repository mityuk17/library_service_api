from fastapi import FastAPI
from v1 import admin_router, librarian_router, user_router, books_router, authorization_router


app = FastAPI()
app.include_router(admin_router.router)
app.include_router(librarian_router.router)
app.include_router(user_router.router)
app.include_router(books_router.router)
app.include_router(authorization_router.router)
