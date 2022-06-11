from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageToEditNotFound

import database
from keyboards import currencies
from keyboards.user import main_keyb
from server import _, bot
from sheet import Sheet

allowed_currencies = {
    "USD": "\u0024",
    "EUR": "\u20AC",
    "GBP": "\u00A3",
    "RUB": "\u20BD",
    "CHF": "CHF",
    "CAD": "CA\u0024",
    "CZK": "\u004B\u010D",
    "BYN": "Br",
    "UAH": "\u20B4",
    "KZT": "\u20B8",
}


class MainCurrencyForm(StatesGroup):
    """This form if used for setting main currency"""

    currency = State()
    format = State()


async def process_cur_cancel(message: Message, state: FSMContext):
    await state.finish()
    await message.answer(_("OK, nex time!"), reply_markup=main_keyb())


async def ask_currency(message: Message):
    # Sending keyboard with available languages
    await message.answer(
        _(
            "What is the main currency of your finances?\n\n"
            "If your currency is not in the list, unfortunately, you will have "
            "to adjust the currency and format manually in the table"
        ),
        reply_markup=currencies.currencies(),
    )

    await MainCurrencyForm.currency.set()


async def ask_format(message: Message, state: FSMContext):
    # Getting currency without emoji
    currency = message.text[-3:]

    if currency not in allowed_currencies.keys():
        await message.answer(
            _(
                "😥 Sorry, this currency cannot be set up through me yet.\n\n"
                "You can do this manually on the Preferences page in your sheet."
            ),
            reply_markup=main_keyb(),
        )
        await state.finish()

    # Saving user currency to memory
    await state.update_data(cur=currency)

    await message.answer(
        _("Please select a currency format that suits you best"),
        reply_markup=currencies.curr_formats(allowed_currencies[currency]),
    )
    await MainCurrencyForm.format.set()


async def update_format(message: Message, state: FSMContext):
    # Getting user currency
    async with state.proxy() as data:
        currency = data["cur"]
    await state.finish()

    # Replacing back currency sign to '{s}'
    pattern = message.text.replace(allowed_currencies[currency], "{s}")

    # If user gave another pattern
    if pattern not in list(currencies.allowed_patterns.keys()):
        await message.answer(
            _(
                "😳 Sorry, I cannot understand this format.\n\n"
                "Change something and try /currency again later"
            ),
            reply_markup=main_keyb(),
        )
        return

    await message.answer(_("Setting main currency..."))

    # Updating currency in sheet
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    try:
        user_sheet.set_main_cur(currency)
    except Exception:
        await message.answer(
            _(
                "😳 Sorry, I cannot understand this format.\n\n"
                "Change something and try /currency again later"
            )
        )
        return

    # Updating formats
    try:
        await bot.edit_message_text(
            _("Updating formats..."), message.chat.id, message.message_id + 1
        )
    except MessageToEditNotFound:
        await bot.send_message(message.chat.id, _("Updating formats..."))

    sym = "$" + allowed_currencies[currency]
    try:
        user_sheet.set_main_cur_format(
            currencies.allowed_patterns[pattern].format(s=sym)
        )
    except Exception:
        await message.answer(
            _(
                "😳 Sorry, I cannot understand this format.\n\n"
                "Change something and try /currency again later"
            ),
        )
        return

    try:
        await bot.delete_message(message.chat.id, message.message_id + 1)
    except MessageToDeleteNotFound:
        pass
    await bot.send_message(message.chat.id, _("Success!"), reply_markup=main_keyb())


def register_maincurrency(dp: Dispatcher):
    dp.register_message_handler(ask_currency, commands=["currency"])
    dp.register_message_handler(
        process_cur_cancel, commands=["cancel"], state=MainCurrencyForm.all_states
    )
    dp.register_message_handler(
        process_cur_cancel,
        lambda msg: msg.text.lower() == "cancel",
        state=MainCurrencyForm.all_states,
    )

    dp.register_message_handler(ask_format, state=MainCurrencyForm.currency)
    dp.register_message_handler(update_format, state=MainCurrencyForm.format)
