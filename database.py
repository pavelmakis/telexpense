import os
import sqlite3

conn = sqlite3.connect(os.path.join("db", "user_sheets.db"))
cursor = conn.cursor()

def get_sheet_url(user_id: str):
    cursor.executemany(
    'SELECT * FROM "user_sheets" '
    f"WHERE user_id={user_id}")
    conn.commit()
    return cursor.fetchone()

def insert_sheet_url(user_id: str, sheet_url: str):
    cursor.execute(
    "INSERT INTO user_sheets ("
    "    user_id, sheet_url"
    f") VALUES ('{user_id}', '{sheet_url}')")
    conn.commit()

def init_if_not_exists():
    """Database initialization"""
    exec_command = '''
    CREATE TABLE IF NOT EXISTS user_sheets (
        user_id     varchar(40) primary key,
        sheet_url   text)
    '''
    cursor.execute(exec_command)
    conn.commit()

init_if_not_exists()