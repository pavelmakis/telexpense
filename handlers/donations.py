import os

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery
from aiogram.types.message import ContentType

import messages
from keyboards import donation, user
from server import bot

PROVIDER_TOKEN = os.getenv("TELEXPENSE_PROVIDER_TOKEN")
PRICE = [LabeledPrice(label="Donate", amount=300)]


class DonationForm(StatesGroup):
    option = State()


async def start_donation(message: Message):
    await message.answer(
        "Where do you want to make the payment from?",
        reply_markup=donation.pay_countries_inlkeyb(),
    )

    # Setting form on option
    await DonationForm.option.set()


async def process_donation_cancel(call: CallbackQuery, state: FSMContext):
    # Answer to query
    await bot.answer_callback_query(call.id)

    # Delete message with inline keyboard
    await bot.delete_message(call.from_user.id, call.message.message_id)

    # Send message with reply markup
    await bot.send_message(
        call.from_user.id,
        "OK, next time",
        reply_markup=user.main_keyb(),
    )

    # End state machine
    await state.finish()


async def process_donation_russia(call: CallbackQuery, state: FSMContext):
    # Answer to query
    await bot.answer_callback_query(call.id)

    # End state machine
    await state.finish()

    # Sending button with payment link
    await bot.edit_message_text(
        messages.russia_donate_message,
        call.from_user.id,
        call.message.message_id,
        reply_markup=donation.ru_donation_link_inlkeyb(),
    )


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
        reply_markup=user.main_keyb(),
    )


async def send_invoice(call: CallbackQuery, state: FSMContext):
    # Answer to query
    await bot.answer_callback_query(call.id)

    # End state machine
    await state.finish()

    # Send help message
    await bot.edit_message_text(
        messages.donate_mes,
        call.from_user.id,
        call.message.message_id,
    )

    # Send invoice
    await bot.send_invoice(
        call.from_user.id,
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
    dp.register_message_handler(start_donation, commands=["donate"])
    dp.register_callback_query_handler(
        process_donation_cancel,
        lambda c: c.data and c.data == "cancel",
        state=DonationForm.all_states,
    )
    dp.register_callback_query_handler(
        process_donation_russia,
        lambda c: c.data and c.data == "russia",
        state=DonationForm.option,
    )
    dp.register_callback_query_handler(
        send_invoice,
        lambda c: c.data and c.data == "other",
        state=DonationForm.option,
    )
    dp.register_pre_checkout_query_handler(
        process_pre_checkout_query, lambda query: True
    )
    dp.register_message_handler(
        process_successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT
    )
