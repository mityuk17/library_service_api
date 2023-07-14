from databases.core import Connection


async def create_tables(session: Connection):
    query = '''CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY ,
            email VARCHAR(50),
            login VARCHAR(50) UNIQUE ,
            password_hash VARCHAR(100),
            role VARCHAR(50),
            active BOOLEAN DEFAULT TRUE);'''
    await session.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS books(
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE,
            author_id INTEGER,
            publisher_id INTEGER,
            genre_id INTEGER,
            reserved_datetime INTEGER DEFAULT 0,
            reserver_id INTEGER DEFAULT NULL,
            in_stock BOOLEAN DEFAULT TRUE, 
            owner_id INTEGER DEFAULT NULL);'''
    await session.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS genres(
            id SERIAL PRIMARY KEY,
            name VARCHAR(20) UNIQUE);'''
    await session.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS authors(
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE);'''
    await session.execute(query)
    query = '''CREATE TABLE IF NOT EXISTS publishers(
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE);'''
    await session.execute(query)
