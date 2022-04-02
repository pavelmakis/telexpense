"""
This file is used for integrate with database where
user sheet URL's are stored.
"""
import os
import sqlite3

conn = sqlite3.connect(os.path.join("db", "user_sheets.db"))
cursor = conn.cursor()

def get_sheet_id(user_id: str) -> str | None:
    """Get users sheet URL by Telegram id"""
    cursor.execute(f'''
    SELECT sheet_id FROM user_sheets
    WHERE user_id='{user_id}'
    ''')
    sheet_id = cursor.fetchone()
    if sheet_id:
        return sheet_id[0]
    return None

def insert_sheet_id(user_id: str, sheet_id: str):
    """Add users sheet URL to database"""
    cursor.execute(f'''
    INSERT INTO user_sheets (
        user_id, sheet_id
    ) VALUES ('{user_id}', '{sheet_id}')
    ''')
    conn.commit()

def delete_sheet_id(user_id: str):
    """Delete record with sheet id"""
    cursor.execute(f'''
    DELETE FROM user_sheets 
    WHERE user_id='{user_id}'
    ''')
    conn.commit()

def is_user_registered(user_id: str) -> bool:
    """Check if users id is in database"""
    if get_sheet_id(user_id):
        return True
    return False

def init_if_not_exists():
    """Database initialization"""
    exec_command = '''
    CREATE TABLE IF NOT EXISTS user_sheets (
        user_id     varchar(40) primary key,
        sheet_id   text)
    '''
    cursor.execute(exec_command)
    conn.commit()

init_if_not_exists()