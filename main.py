import json
import time
import fastapi
from fastapi import FastAPI, Request, HTTPException
import db


app = FastAPI()


@app.on_event('startup')
async def startup():
    await db.database.connect()
    await db.create_tables()


@app.on_event('shutdown')
async def shutdown():
    await db.database.disconnect()


@app.get("/")
async def root():
    return {"status": "OK"}


@app.get('/api/admin/users')
async def get_users(request: Request):
    """
    Get all users
    :param request: Request object with json(required params: login, password)
    :return:list of users
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return HTTPException(status_code=400, detail='JSON not provided')
    login = data.get('login')
    password = data.get('password')
    admin = await db.get_user(login=login)
    if not admin:
        return HTTPException(status_code=404, detail='Admin not found')
    if not admin.validate_password(password):
        return HTTPException(status_code=401, detail='Invalid password')
    if admin.role != 'admin':
        return HTTPException(status_code=403, detail='You are not an admin')
    users = await db.get_users()
    return [user.to_data_dict() for user in users]


@app.post('/api/admin/users')
async def create_user(request: Request):
    """
    Create a new User object
    :param request: Request object with json(required params: login, password, new_user_data)
    :return:
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return HTTPException(status_code=400, detail='JSON not provided')
    login = data.get('login')
    password = data.get('password')
    admin = await db.get_user(login=login)
    if not admin:
        return HTTPException(status_code=404, detail='Admin not found')
    if not admin.validate_password(password):
        return HTTPException(status_code=401, detail='Invalid password')
    if admin.role != 'admin':
        return HTTPException(status_code=403, detail='You are not an admin')
    new_user_data = data.get('new_user_data')
    if not new_user_data:
        return HTTPException(status_code=400, detail='No new user data')
    await db.insert_user(new_user_data)
    return fastapi.Response()


@app.put('/api/admin/users')
async def change_user_data(request: Request):
    """
    Changes User object's fields' values
    :param request: Request object with json(required params: login, password, user_data)
    :return:
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return HTTPException(status_code=400, detail='JSON not provided')
    login = data.get('login')
    password = data.get('password')
    admin = await db.get_user(login=login)
    if not admin:
        return HTTPException(status_code=404, detail='User not found')
    if not admin.validate_password(password):
        return HTTPException(status_code=401, detail='Invalid password')
    if admin.role != 'admin':
        return HTTPException(status_code=403, detail='You are not an admin')
    user_data = data.get('user_data')
    if not user_data:
        return HTTPException(status_code=400, detail='No user data')
    user_id = user_data.get('id')
    if not user_id:
        return HTTPException(status_code=400, detail='No user id')
    user = await db.get_user(user_id=user_id)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    user = user.to_data_dict()
    for item in user_data:
        user[item] = user_data[item]
    del user['role']
    await db.update_user(user)
    return fastapi.Response()


@app.get('/api/admin/users/{user_id}')
async def get_user_info(user_id: int, request: Request):
    """
    Gets user by id
    :param user_id:
    :param request: Request object with json(required params: login, password)
    :return: dict with User params
    """
    try:
        print(await request.body())
        data = await request.json()

    except json.JSONDecodeError:
        return HTTPException(status_code=400, detail='JSON not provided')
    login = data.get('login')
    password = data.get('password')
    admin = await db.get_user(login=login)
    print(admin)
    if not admin:
        return HTTPException(status_code=404, detail='User not found')
    if not admin.validate_password(password):
        print(password, admin.password)
        return HTTPException(status_code=401, detail='Invalid password')
    if admin.role != 'admin':
        return HTTPException(status_code=403, detail='You are not an admin')
    user = await db.get_user(user_id)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    return user.to_data_dict()


@app.delete('/api/admin/users/{user_id}')
async def delete_user(user_id: int, request: Request):
    """
    Deletes user from database
    :param user_id:
    :param request: Request object with json(required params: login, password)
    :return:
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return HTTPException(status_code=400, detail='JSON not provided')
    login = data.get('login')
    password = data.get('password')
    admin = await db.get_user(login=login)
    if not admin:
        return HTTPException(status_code=404, detail='User not found')
    if not admin.validate_password(password):
        return HTTPException(status_code=401, detail='Invalid password')
    if admin.role != 'admin':
        return HTTPException(status_code=403, detail='You are not an admin')
    await db.delete_user(user_id)
    return fastapi.Response()


@app.post('/api/librarian/books')
async def create_book(request: Request):
    """
    Creates Book object
    :param request: Request object with json(required params: login, password, new_book_data)
    :return:
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return HTTPException(status_code=400, detail='JSON not provided')
    login = data.get('login')
    password = data.get('password')
    librarian = await db.get_user(login=login)
    if not librarian:
        return HTTPException(status_code=404, detail='User not found')
    if not librarian.validate_password(password):
        return HTTPException(status_code=401, detail='Invalid password')
    if librarian.role != 'librarian':
        return HTTPException(status_code=403, detail='You are not a librarian')
    new_book_data = data.get('new_book_data')
    author_name = new_book_data.get('author')
    author_id = await db.get_author(author_name=author_name)
    if not author_id:
        author_id = await db.insert_genre(author_name)
    genre_name = new_book_data.get('genre')
    genre_id = await db.get_genre(genre_name=genre_name)
    if not genre_id:
        genre_id = await db.insert_genre(genre_name)
    publisher_name = new_book_data.get('publisher')
    publisher_id = await db.get_publisher(publisher_name=publisher_name)
    if not publisher_id:
        publisher_id = await db.insert_publisher(publisher_name)
    new_book_data['author_id'] = author_id
    new_book_data['publisher_id'] = publisher_id
    new_book_data['genre_id'] = genre_id
    await db.insert_book(new_book_data)
    return fastapi.Response()


@app.put('/api/librarian/books')
async def change_book_data(request: Request):
    """
    Changes Book object's fields' values
    :param request: Request object with json(required params: login, password, book_data)
    :return:
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return HTTPException(status_code=400, detail='JSON not provided')
    login = data.get('login')
    password = data.get('password')
    librarian = await db.get_user(login=login)
    if not librarian:
        return HTTPException(status_code=404, detail='User not found')
    if not librarian.validate_password(password):
        return HTTPException(status_code=401, detail='Invalid password')
    if librarian.role != 'librarian':
        return HTTPException(status_code=403, detail='You are not a librarian')
    book_data = data.get('book_data')
    if not book_data:
        return HTTPException(status_code=400, detail='No book data provided')
    user_id = book_data.get('id')
    if not user_id:
        return HTTPException(status_code=400, detail='No user id provided')
    book = await db.get_book(book_id=user_id)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    book = book.to_data_dict()
    for item in book_data:
        book[item] = book_data[item]
    await db.update_user(book)
    return fastapi.Response()


@app.get('/api/librarian/books/{book_id}')
async def get_book_info(book_id: int, request: Request):
    """
    Get book by id
    :param book_id:
    :param request: Request object with json(required params: login, password)
    :return: dict with Book object params
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return HTTPException(status_code=400, detail='JSON not provided')
    login = data.get('login')
    password = data.get('password')
    librarian = await db.get_user(login=login)
    if not librarian:
        return HTTPException(status_code=404, detail='User not found')
    if not librarian.validate_password(password):
        return HTTPException(status_code=401, detail='Invalid password')
    if librarian.role != 'librarian':
        return HTTPException(status_code=403, detail='You are not a librarian')
    book = await db.get_book(book_id=book_id)
    if book:
        return book.to_data_dict()
    else:
        return HTTPException(status_code=400, detail='Book not found')


@app.delete('/api/librarian/books/{book_id}')
async def delete_book(book_id: int, request: Request):
    """
    Delete book from database
    :param book_id:
    :param request: Request object with json(required params: login, password)
    :return:
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return HTTPException(status_code=400, detail='JSON not provided')
    login = data.get('login')
    password = data.get('password')
    librarian = await db.get_user(login=login)
    if not librarian:
        return HTTPException(status_code=404, detail='User not found')
    if not librarian.validate_password(password):
        return HTTPException(status_code=401, detail='Invalid password')
    if librarian.role != 'librarian':
        return HTTPException(status_code=403, detail='You are not an admin')
    await db.delete_book(book_id)
    return fastapi.Response()


@app.get('/api/books')
async def get_books():
    """
    Gives all books
    :return: list of dicts with Book object's params
    """
    books = await db.search_books()
    return [book.to_data_dict() for book in books]


@app.get('/api/books/{book_id}')
async def get_book(book_id: int):
    """
    Get book by its id
    :param book_id:
    :return: dict with Book object params
    """
    book = await db.get_book(book_id=book_id)
    if book:
        return book.to_data_dict()
    else:
        return HTTPException(status_code=404, detail='Book not found')


@app.get('/api/books/genre/{genre_id}')
async def search_books_by_genre(genre_id: int):
    """
    Gets books specified by genre
    :param genre_id:
    :return: list of dicts with Book object's params
    """
    genre = await db.get_genre(genre_id=genre_id)
    if not genre:
        return HTTPException(status_code=404, detail='Genre not found')
    books = await db.search_books(genre_id=genre_id)
    return [book.to_data_dict() for book in books]


@app.get('/api/books/publisher/{publisher_id}')
async def search_books_by_publisher(publisher_id: int):
    """
    Gets books specified by publisher
    :param publisher_id:
    :return: list of dicts with Book object's params
    """
    publisher = await db.get_publisher(publisher_id=publisher_id)
    if not publisher:
        return HTTPException(status_code=404, detail='Publisher not found')
    books = await db.search_books(publisher_id=publisher_id)
    return [book.to_data_dict() for book in books]


@app.get('/api/books/author/{author_id}')
async def search_books_by_author(author_id: int):
    """
    Gets books specified by author
    :param author_id:
    :return: list of dicts with Book object's params
    """
    author = await db.get_author(author_id=author_id)
    if not author:
        return HTTPException(status_code=404, detail='Publisher not found')
    books = await db.search_books(author_id=author_id)
    return [book.to_data_dict() for book in books]


@app.get('/api/reserve_book/{book_id}')
async def reserve_book(book_id: int, request: Request):
    """
    Reserves book and make it unavailable to reserve or take it by other users
    :param book_id:
    :param request: Request object with json(required params: login, password)
    :return:
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return HTTPException(status_code=400, detail='JSON not provided')
    login = data.get('login')
    password = data.get('password')
    user = await db.get_user(login=login)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    if not user.validate_password(password):
        return HTTPException(status_code=401, detail='Invalid password')
    if user.role != 'user':
        return HTTPException(status_code=403, detail='You are not a user')
    book = await db.get_book(book_id=book_id)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    if book.is_reserved():
        return HTTPException(status_code=403, detail='Book is already reserved')
    if not book.in_stock:
        return HTTPException(status_code=403, detail='Book is not in stock')
    book.reserved_datetime = int(time.time())
    book.reserved_user_id = user.id
    await db.update_book(book_data=book.to_data_dict())
    return fastapi.Response()


@app.get('/api/librarian/give_book')
async def give_book(request: Request):
    """
    Makes book unavailable for reserving of taking by users
    :param request: Request object with json(required params: login, password, book_id, user_id)
    :return:
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return HTTPException(status_code=400, detail='JSON not provided')
    login = data.get('login')
    password = data.get('password')
    librarian = await db.get_user(login=login)
    if not librarian:
        return HTTPException(status_code=404, detail='Librarian not found')
    if not librarian.validate_password(password):
        return HTTPException(status_code=401, detail='Invalid password')
    if librarian.role != 'librarian':
        return HTTPException(status_code=403, detail='You are not a librarian')
    book_id = data.get('book_id')
    book = await db.get_book(book_id=book_id)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    user_id = data.get('user_id')
    user = await db.get_user(user_id)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    if book.is_reserved() and book.reserved_user_id != user_id:
        return HTTPException(status_code=403, detail='Book is reserved by other user')
    if not book.in_stock:
        return HTTPException(status_code=403, detail='Book is not in stock')
    book.in_stock = False
    book.owner_id = user_id
    await db.update_book(book_data=book.to_data_dict())
    return fastapi.Response()


@app.get('/api/librarian/take_book')
async def take_book(request: Request):
    """
    Makes book available for reserving and taking by users
    :param request: Request object with json(required params: login, password, book_id)
    :return:
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return HTTPException(status_code=400, detail='JSON not provided')
    login = data.get('login')
    password = data.get('password')
    librarian = await db.get_user(login=login)
    if not librarian:
        return HTTPException(status_code=404, detail='Librarian not found')
    if not librarian.validate_password(password):
        return HTTPException(status_code=401, detail='Invalid password')
    if librarian.role != 'librarian':
        return HTTPException(status_code=403, detail='you are not a librarian')
    book_id = data.get('book_id')
    book = await db.get_book(book_id=book_id)
    if not book:
        return HTTPException(status_code=404, detail='Book not found')
    if book.in_stock:
        return HTTPException(status_code=403, detail='Book is already in stock')
    book.in_stock = True
    await db.update_book(book.to_data_dict())
    return fastapi.Response()
