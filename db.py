import sqlite3

def execute_query(query, params=()):
    with sqlite3.connect("data/salat.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

def fetch_query(query, params=()):
    with sqlite3.connect("data/salat.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def fetch_one(query, params=()):
    with sqlite3.connect("data/salat.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

def close_db():
    sqlite3.connect("data/salat.db").close()

def drop_db(tables: list[str]):
    for table in tables:
        execute_query(f'DROP TABLE IF EXISTS {table}')

def init_db(schemas: dict[str, str]):
    for table, schema in schemas.items():
        drop_db([table])
        execute_query(f'CREATE TABLE IF NOT EXISTS {table} ({schema})')