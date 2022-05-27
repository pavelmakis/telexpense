from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

import database
import keyboards
import messages
from keyboards import get_main_markup, get_register_markup
from sheet import Sheet

unregistered = lambda message: not database.is_user_registered(message.from_user.id)


async def cmd_start(message: Message):
    """This handler is called when user sends `/start` command."""
    # If user is registered, show main keyboard,
    # if not - 'register' button
    is_registered = database.is_user_registered(message.from_user.id)
    await message.answer(
        messages.start_message,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=get_main_markup() if is_registered else get_register_markup(),
    )


async def cmd_help(message: Message):
    """This handler is called when user sends /help command."""
    # TODO: Create different help message for unregistered users
    await message.reply(
        messages.help,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=keyboards.get_main_markup(),
    )


def register_start_help(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_message_handler(cmd_help, commands=["help"])


async def answer_unregistered(message: Message):
    """This handler is used to answer to unregistered users."""
    await message.answer(
        "I can only work with registered users!\nRead the wiki or type /register",
        reply_markup=get_register_markup(),
    )


async def cmd_cancel(message: Message, state: FSMContext):
    """This handler is called to cancel states."""
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "Can cancel only while you are filling a record form.\n\n"
            + "Nothing to cancel now!",
            reply_markup=get_main_markup(),
        )
    else:
        # Cancel state and inform user about it
        await state.finish()
        await message.answer(
            "Cancelled",
            reply_markup=get_main_markup(),
        )


async def cmd_available(message: Message):
    """Send a list of accounts and its amounts from users sheet"""
    # Openning sheet, checking for errors
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    if user_sheet == None:
        await message.answer(messages.error_message, reply_markup=get_main_markup())
        return

    amounts = user_sheet.get_account_amounts()
    max_text_lenght, max_digit_lenght = 0, 0

    # Finding account with the longest name and
    # the longest amount (in symbols)
    for i in range(len(amounts)):
        if len(amounts[i][0]) > max_text_lenght:
            max_text_lenght = len(amounts[i][0])
        if len(amounts[i][1]) > max_digit_lenght:
            max_digit_lenght = len(amounts[i][1])

    # Combining answer string
    # ``` is used for parsing string in markdown to get
    # fixed width in message
    available = "💰 Your accounts:\n\n"
    available += "```\n"
    for i in range(len(amounts) - 1):
        # Current line lenght
        text_lenght = len(amounts[i][0]) + len(amounts[i][1])
        available += amounts[i][0]
        # max_text_lenght + max_digit_lenght is the longest line
        # 2 (spaces) is the indent between account column and amount column
        available += " " * (max_text_lenght + max_digit_lenght - text_lenght + 2)
        available += amounts[i][1] + "\n"
    available += "```"

    # Adding "Daily available" from last item from get func
    available += "\n*Daily available:*   "
    available += "`" + amounts[-1] + "`"

    await message.answer(
        available, parse_mode="MarkdownV2", reply_markup=get_main_markup()
    )


async def undo_transaction(message: Message):
    """This handler is used to delete last transaction from user's sheet."""
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    await message.answer("Wait a second...")

    # Getting last transaction type
    last_tran_type = user_sheet.get_last_transaction_type()
    if last_tran_type == None:
        await message.answer("🤔 Looks like there is no transactions...")
        return

    # Delete last transaction
    user_sheet.delete_last_transaction(last_tran_type)

    await message.answer("👌 Successfully deleted last transaction!")


def register_user(dp: Dispatcher):
    dp.register_message_handler(
        answer_unregistered, unregistered, content_types=["any"]
    )
    dp.register_message_handler(cmd_cancel, commands=["cancel"], state="*")
    dp.register_message_handler(
        cmd_cancel, lambda msg: msg.text.lower() == "cancel", state="*"
    )
    dp.register_message_handler(cmd_available, commands=["available"])
    dp.register_message_handler(
        cmd_available, lambda message: message.text.startswith("💲Available")
    )
    dp.register_message_handler(undo_transaction, commands=["undo"])
