import os

from aiogram import Dispatcher
from aiogram.types import LabeledPrice, Message

PROVIDER_TOKEN = os.getenv("TELEXPENSE_PROVIDER_TOKEN")
PRICE = [LabeledPrice(label="Donate", amount=300)]

import answers
from keyboards import get_main_markup


async def send_invoice(message: Message):
    # Send help message
    await message.answer(answers.donate_mes, reply_markup=get_main_markup())
    # Send invoice
    await message.answer(
        message.chat.id,
        title="Donation to developer",
        description=answers.donate_description,
        provider_token=PROVIDER_TOKEN,
        currency="eur",
        is_flexible=False,
        prices=PRICE,
        max_tip_amount=9700,
        suggested_tip_amounts=[200, 700, 1200, 1700],
        payload="Donate invoice sent",
    )


def register_user(dp: Dispatcher):
    dp.register_message_handler(send_invoice, commands=["donate"])
