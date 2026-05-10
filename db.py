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

def init_db():
    execute_query('''
        CREATE TABLE IF NOT EXISTS cookies (
            name TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    execute_query('''
        CREATE TABLE IF NOT EXISTS provinces (
            value TEXT PRIMARY KEY,
            name TEXT,
            name_slug TEXT
        )
    ''')
        
def close_db():
    sqlite3.connect("data/salat.db").close()

def remove_db():
    execute_query('DELETE FROM cookies')
    execute_query('DELETE FROM provinces')