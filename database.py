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
        user_id, sheet_id, language
    ) VALUES ('{user_id}', '{sheet_id}', 'en')
    """
    )
    conn.commit()


def get_all_users() -> list:
    """Get all users as list"""
    cursor.execute(f"SELECT user_id FROM bot_users")
    data, users = cursor.fetchall(), []
    for user in data:
        users.append(int(user[0]))

    return users


def get_users_by_language(lang: str) -> list[int]:
    """Get user list by language"""
    cursor.execute(f'SELECT user_id FROM bot_users WHERE language = "{lang}"')
    data, users = cursor.fetchall(), []

    if data != None:
        for user in data:
            users.append(int(user[0]))
        return users
    return None


def get_user_count() -> int:
    """Get user count"""
    cursor.execute("SELECT COUNT(user_id) FROM bot_users")
    count = cursor.fetchone()

    return count[0]


def update_language(user_id: str, lang: str):
    """Update users language"""
    cursor.execute(
        f'UPDATE bot_users SET language = "{lang}" WHERE user_id ="{user_id}"'
    )
    conn.commit()


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
        user_id    varchar(40) primary key,
        sheet_id   text,
        language   varchar(10))
    """
    cursor.execute(exec_command)
    conn.commit()


init_if_not_exists()
