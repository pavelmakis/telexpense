from asyncpg import create_pool
from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER, DB_PORT


async def open_pool() -> None:
    global pool

    pool = await create_pool(
        dsn=f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        min_size=50,
        max_size=1000,
        timeout=10,
        max_inactive_connection_lifetime=10,
    )


async def close_pool() -> None:
    await pool.close()
