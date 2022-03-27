"""
This file is used for integrate with database where
user sheet URL's are stored.
"""
import os
import sqlite3

conn = sqlite3.connect(os.path.join("db", "user_sheets.db"))
cursor = conn.cursor()

def get_sheet_url(user_id: str):
    """Get users sheet URL by Telegram id"""
    cursor.executemany(f'''
    SELECT * FROM user_sheets
    WHERE user_id={user_id}
    ''')
    return cursor.fetchone()

def insert_sheet_url(user_id: str, sheet_url: str):
    """Add users sheet URL to database"""
    cursor.execute(f'''
    INSERT INTO user_sheets (
        user_id, sheet_url"
    ) VALUES ('{user_id}', '{sheet_url}')
    ''')
    conn.commit()

def is_user_registered(user_id: str) -> bool:
    """Check if users id is in database"""
    if get_sheet_url(user_id):
        return True
    return False

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