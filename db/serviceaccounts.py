from asyncpg import Connection
from ujson import loads as ujson_loads


class ServiceAccountsDAL:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    async def get_less_used_account(self) -> dict:
        """This method get service account credentials with
        which were used minimum times.

        Returns:
            dict: service account credentials
        """

        s_account = await self.connection.fetchval(
            """SELECT data FROM service_accounts 
            ORDER BY times_used ASC
            LIMIT 1"""
        )

        return ujson_loads(s_account)

    async def update_times_used(self, email: str) -> None:
        """This method updates 'times_used' parameter for
        service account with given id.
        """

        await self.connection.execute(
            """UPDATE service_accounts
            SET times_used = times_used + 1
                WHERE email = $1""",
            email,
        )
