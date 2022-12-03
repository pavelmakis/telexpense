import asyncio
import logging

# import sentry_sdk
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web
from aiohttp.web import Application

# from sentry_sdk.integrations.aiohttp import AioHttpIntegration
# from sentry_sdk.integrations.logging import LoggingIntegration

import config
from db import PostgresConnector

# if not config.DEBUG:
#     sentry_sdk.init(
#         dsn=config.SENTRY_DSN,
#         environment=config.ENVIRONMENT,
#         traces_sample_rate=0.1,
#         integrations=[
#             AioHttpIntegration(),
#             LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
#         ],
#     )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] : #%(levelname)-8s - %(filename)s:%(lineno)d - %(name)s - %(message)s",
)


def register_all_middlewares(dp: Dispatcher) -> None:
    pass


def register_all_filters(dp: Dispatcher) -> None:
    # dp.bind_filter(IsAdmin)
    pass


def register_all_handlers(dp: Dispatcher) -> None:
    register_start(dp)
    register_expense(dp)


async def on_startup(app: Application) -> None:
    bot_info = await bot.get_me()
    logging.info(f"🤙 Hello from {bot_info.full_name} [@{bot_info.username}]!")

    # Setting webhook URL
    await bot.set_webhook(url=config.WEBHOOK_URL)
    logging.info(f"Webhook was set on '{config.WEBHOOK_URL}'")

    # Openning connection pool
    await pg_pool.open_pool()


async def on_shutdown(app: Application) -> None:
    # Disconecting redis storage
    await dp.storage.close()
    await dp.storage.wait_closed()

    # Closing connection pool
    await pg_pool.close_pool()


# Initialize storage
storage = RedisStorage2(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    prefix="telexpense_fsm",
)

# Initialize bot and dispatcher
bot = Bot(token=config.API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)

# Initialize postgres connection pool
pg_pool = PostgresConnector()


if __name__ == "__main__":
    # from core.filters.isadmin import IsAdmin
    from telexpense.handlers.expense import register_expense
    from telexpense.handlers.start import register_start

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    bot_app = get_new_configured_app(dispatcher=dp, path=config.WEBHOOK_URL)
    bot_app.on_startup.append(on_startup)
    bot_app.on_shutdown.append(on_shutdown)

    # Adding route for handling payment requests
    # app.add_routes([web.post("/{project_name}/prodamus", prodamus)])
    # logging.info("Route for payments added on '/{project_name}/prodamus'")

    web.run_app(
        app=bot_app,
        host=config.WEBAPP_HOST,
        port=config.WEBAPP_PORT,
    )
