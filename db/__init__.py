from asyncpg import Pool, create_pool
from asyncpg.pool import PoolAcquireContext

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


class PostgresConnector:
    def __init__(self) -> None:
        self.pool: Pool = None

    async def open_pool(self) -> None:
        self.pool = await create_pool(
            dsn=f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
            min_size=50,
            max_size=100,
            timeout=10,
            max_inactive_connection_lifetime=10,
        )

    async def acquire(self) -> PoolAcquireContext:
        return self.pool.acquire()

    async def close_pool(self) -> None:
        if self.pool is not None:
            await self.pool.close()
