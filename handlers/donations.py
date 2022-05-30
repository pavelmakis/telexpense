import os

from aiogram import Dispatcher
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery
from aiogram.types.message import ContentType

from server import bot

PROVIDER_TOKEN = os.getenv("TELEXPENSE_PROVIDER_TOKEN")
PRICE = [LabeledPrice(label="Donate", amount=300)]

import messages
from keyboards import get_main_markup


# I have a simple donate button, so I answer OK to query
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def process_successful_payment(message: Message):
    """Sends thanks message if successfull payment"""
    await bot.send_message(
        message.chat.id,
        messages.successfull_payment.format(
            total_amount=message.successful_payment.total_amount // 100,
            currency=message.successful_payment.currency,
        ),
        parse_mode="Markdown",
        reply_markup=get_main_markup(),
    )


async def send_invoice(message: Message):
    # Send help message
    await message.answer(messages.donate_mes, reply_markup=get_main_markup())
    # Send invoice
    await bot.send_invoice(
        message.chat.id,
        title="Donation to developer",
        description=messages.donate_description,
        provider_token=PROVIDER_TOKEN,
        currency="eur",
        is_flexible=False,
        prices=PRICE,
        max_tip_amount=9700,
        suggested_tip_amounts=[200, 700, 1200, 1700],
        payload="Donate invoice sent",
    )


def register_donations(dp: Dispatcher):
    dp.register_message_handler(send_invoice, commands=["donate"])
    dp.register_pre_checkout_query_handler(
        process_pre_checkout_query, lambda query: True
    )
    dp.register_message_handler(
        process_successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT
    )
