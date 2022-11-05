from aiogram.types import Message
from aiogram import Dispatcher


async def answer_start_cmd(msg) -> None:
    await msg.answer("Hello")


def register_start(dp: Dispatcher) -> None:
    dp.register_message_handler(answer_start_cmd, commands=["start"])
