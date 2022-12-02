import logging
from datetime import datetime
from enum import Enum
from uuid import UUID

import sentry_sdk
from asyncpg import Connection
from ujson import loads as ujson_loads


class Locale(Enum):
    en_US = "en_US"
    ru_RU = "ru_RU"


class UsersDAL:
    def __init__(self, connection: Connection) -> bool:
        self.connection = connection

    async def add_user(self, user_id: int, username: str, first_name: str) -> None:
        """This method add user to database."""

        try:
            await self.connection.execute(
                """INSERT INTO users (id, username, first_name)
                VALUES ($1, $2, $3)""",
                user_id,
                username,
                first_name,
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False

        return True

    async def set_locale(self, user_id: int, locale: Locale) -> None:
        """This method updates user's language_code field to
        given locale.

        Args:
            locale (Locale): locale code
        """

        await self.connection.execute(
            "UPDATE users SET language_code = $1 WHERE id = $2", locale.value, user_id
        )

    async def set_last_action(self, user_id: int) -> None:
        """This method updates user's 'last_action_at' field
        to current time.
        """

        await self.connection.execute(
            "UPDATE users SET last_action_at = CURRENT_TIMESTAMP WHERE id = $1", user_id
        )

    async def set_is_active(self, user_id: int, is_active: bool = False) -> None:
        """This method updates 'is_active' field for given user.

        Args:
            is_active (bool, optional): 'is_active' field value. Defaults to False.
        """

        await self.connection.execute(
            "UPDATE users SET is_active = $1 WHERE id = $2", is_active, user_id
        )

    async def set_username(self, user_id: int, new_username: str) -> None:
        """This method update user's username."""

        await self.connection.execute(
            "UPDATE users SET username = $1 WHERE id = $2", new_username, user_id
        )

    async def set_first_name(self, user_id: int, new_first_name: str) -> None:
        """This method update user's first name."""

        await self.connection.execute(
            "UPDATE users SET first_name = $1 WHERE id = $2", new_first_name, user_id
        )

    async def get_locale(self, user_id: int) -> Locale:
        """This method gets user's locale (language_code).
        If user or locale not specified, english locale is returned.
        """

        locale = await self.connection.fetchval(
            "SELECT language_code FROM users WHERE id = $1", user_id
        )

        try:
            locale = Locale(locale)
        except ValueError:
            locale = Locale.en_US
        finally:
            return locale

    async def get_invite_code(self, user_id: int) -> UUID:
        """This method gets user's invite code.

        Returns:
            UUID: user's invite code.
        """

        invite_code = await self.connection.fetchval(
            "SELECT invite_code FROM users WHERE id = $1", user_id
        )

        return invite_code

    async def get_subscription_end(self, user_id: int) -> datetime | None:
        """This method gets user's subscriptions end time.

        Returns:
            datetime | None: time when subscription ends or None
            if user has no subscription.
        """

        sub_end = await self.connection.fetchval(
            "SELECT subscription_ends_at FROM users WHERE id = $1", user_id
        )

        return sub_end

    async def get_service_account(self, user_id: int) -> dict:
        """This method returns service account credentials which are used
        by user to access his spreadsheet from bot.

        Returns:
            dict: service account credentials.
        """

        s_account = await self.connection.fetchval(
            "SELECT service_account FROM users WHERE id = $1", user_id
        )

        if s_account is not None:
            return ujson_loads(s_account)
