from databases.core import Connection
import databases.backends.postgres
from app.schemas import users


databases.backends.postgres.Record.__iter__ = lambda self: iter(self._row)


async def get_user_by_id(user_id: int, session: Connection) -> users.User:
    query = '''SELECT * FROM users WHERE id = :id'''
    result = await session.fetch_one(query=query, values={'id': user_id})
    return users.User.from_orm(result) if result else None


async def get_no_password_user_by_id(user_id: int, session: Connection) -> users.NoPasswordUser:
    query = '''SELECT id, email, login, role, active FROM users;'''
    result = await session.fetch_one(query=query, values={'id': user_id})
    return users.NoPasswordUser.from_orm(result) if result else None


async def get_user_by_login(login: str, session: Connection) -> users.User:
    query = '''SELECT * FROM users WHERE login = :login;'''
    result = await session.fetch_one(query=query, values={'login': login})
    return users.User.from_orm(result) if result else None


async def get_users(session: Connection) -> list[users.NoPasswordUser]:
    query = '''SELECT id, email, login, role, active FROM users;'''
    result = await session.fetch_all(query=query)
    all_users = [users.NoPasswordUser.from_orm(user_data) for user_data in result]
    return all_users


async def insert_user(user_data: users.NewUserData, session: Connection):
    query = '''INSERT INTO users(email, login, password_hash, role) VALUES 
    (:email, :login, :password, :role);'''
    values = user_data.dict()
    await session.execute(query=query, values=values)


async def update_user(user_data: users.User, session: Connection):
    query = '''UPDATE users SET email = :email, login = :login, password_hash = :password_hash,
    active = :active, role = :role WHERE id = :id;'''
    values = user_data.dict()
    await session.execute(query=query, values=values)


async def delete_user(user_id: int, session: Connection):
    query = '''DELETE FROM users WHERE id = :id'''
    await session.execute(query, {'id': user_id})
