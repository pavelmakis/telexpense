"""
This file is used for integrate with database where
user sheet id's are stored.
"""
import os
import sqlite3

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "db", "user_sheets.db"))
cursor = conn.cursor()


def get_sheet_id(user_id: str) -> str | None:
    """Get users Google Sheet id by Telegram id"""
    cursor.execute(
        f"""
    SELECT sheet_id FROM bot_users
    WHERE user_id='{user_id}'
    """
    )
    sheet_id = cursor.fetchone()
    if sheet_id:
        return sheet_id[0]
    return None


def insert_sheet_id(user_id: str, sheet_id: str):
    """Add users Google Sheet id to database"""
    cursor.execute(
        f"""
    INSERT INTO bot_users (
        user_id, sheet_id
    ) VALUES ('{user_id}', '{sheet_id}')
    """
    )
    conn.commit()


def get_all_users() -> list:
    cursor.execute(f"SELECT user_id FROM bot_users")
    data, users = cursor.fetchall(), []
    for user in data:
        users.append(int(user[0]))

    return users


def delete_sheet_id(user_id: str):
    """Delete record with Google Sheet id"""
    cursor.execute(
        f"""
    DELETE FROM bot_users 
    WHERE user_id='{user_id}'
    """
    )
    conn.commit()


def is_user_registered(user_id: str) -> bool:
    """Check if users Telegram id is in database"""
    if get_sheet_id(user_id):
        return True
    return False


def init_if_not_exists():
    """Initialize the database"""
    exec_command = """
    CREATE TABLE IF NOT EXISTS bot_users (
        user_id     varchar(40) primary key,
        sheet_id   text)
    """
    cursor.execute(exec_command)
    conn.commit()


init_if_not_exists()
