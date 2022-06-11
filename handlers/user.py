from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.utils.exceptions import MessageToEditNotFound

import database
from keyboards.user import main_keyb, register_keyb
from server import _, bot
from sheet import Sheet

unregistered = lambda message: not database.is_user_registered(message.from_user.id)
BOT_WIKI = "https://github.com/pavelmakis/telexpense/wiki"


async def cmd_start(message: Message):
    """This handler is called when user sends `/start` command."""
    # If user is registered, show main keyboard,
    # if not - 'register' button
    is_registered = database.is_user_registered(message.from_user.id)
    await message.answer(
        _(
            "Hi! I'm Telexpense bot 📺\n\n"
            "I can help you manage your finances in Google Sheet.\n"
            "If you are a new user, read the [wiki]({wiki}) "
            "or type /register to start using me".format(wiki=BOT_WIKI)
        ),
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=main_keyb() if is_registered else register_keyb(),
    )


async def cmd_help(message: Message):
    """This handler is called when user sends /help command."""
    # TODO: Create different help message for unregistered users
    await message.reply(
        _(
            "I can help you manage your finances in Google Sheet.\n\n"
            "If you don't understand something, check out [this wiki]({wiki})\n\n"
            "I can understand these commands:\n\n"
            "*Add records*\n"
            "/expense (➖Expense) - add new expense\n"
            "/income (➕Income) - add new income\n"
            "/transfer (💱Transfer) - add new transfer\n"
            "/cancel - cancel record filling\n"
            "/addexp - add expense in a single message\n"
            "/addinc - add income in a single message\n"
            "/addtran - add transaction in a single message\n\n"
            "*Show balance*\n"
            "/available (💲Available) - show your accounts balances\n\n"
            "*Revert changes*\n"
            "/undo - delete last transaction from Google Sheet\n\n"
            "*Settings*\n"
            "/currency - set main currency and its format\n"
            "/language - set bot's language\n"
            "/register - connect me to Google Sheet or change connected sheet\n\n"
            "*Other*\n"
            "/donate - sponsor this project".format(wiki=BOT_WIKI)
        ),
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=main_keyb(),
    )


def register_start_help(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_message_handler(cmd_help, commands=["help"])


async def answer_unregistered(message: Message):
    """This handler is used to answer to unregistered users."""
    await message.answer(
        _(
            "I can only work with registered users!\n"
            "Read the [wiki]({wiki}) or type /register".format(wiki=BOT_WIKI)
        ),
        reply_markup=register_keyb(),
    )


async def cmd_cancel(message: Message, state: FSMContext):
    """This handler is called to cancel states."""
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            _("Can cancel only while filling a form.\n\nNothing to cancel now!"),
            reply_markup=main_keyb(),
        )
    else:
        # Cancel state and inform user about it
        await state.finish()
        await message.answer(
            _("Cancelled"),
            reply_markup=main_keyb(),
        )


async def cmd_available(message: Message):
    """Send a list of accounts and its amounts from users sheet"""
    # Openning sheet, checking for errors
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    if user_sheet == None:
        await message.answer(
            _(
                "😳 Something went wrong...\n\n"
                "Please try again later.\n"
                "If it does not work again, check your table or add it again via /register. "
                "Maybe you have changed the table and I can no longer work with it"
            ),
            reply_markup=main_keyb(),
        )
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
    available = _("💰 Your accounts:\n\n")
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
    available += _("\n*Daily available:*   ")
    available += "`" + amounts[-1] + "`"

    await message.answer(available, parse_mode="MarkdownV2", reply_markup=main_keyb())


async def undo_transaction(message: Message):
    """This handler is used to delete last transaction from user's sheet."""
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    await message.answer(_("Wait a second..."))

    # Getting last transaction type
    last_tran_type = user_sheet.get_last_transaction_type()
    if last_tran_type == None:
        try:
            await bot.edit_message_text(
                _("🤔 Looks like there is no transactions..."),
                message.chat.id,
                message.message_id + 1,
            )
        except MessageToEditNotFound:
            await message.answer(_("🤔 Looks like there is no transactions..."))

        return

    # Delete last transaction
    user_sheet.delete_last_transaction(last_tran_type)

    try:
        await bot.edit_message_text(
            _("👌 Successfully deleted last transaction!"),
            message.chat.id,
            message.message_id + 1,
        )
    except MessageToEditNotFound:
        await message.answer(_("👌 Successfully deleted last transaction!"))


def register_user(dp: Dispatcher):
    dp.register_message_handler(
        answer_unregistered, unregistered, content_types=["any"]
    )
    dp.register_message_handler(cmd_cancel, commands=["cancel"], state="*")
    dp.register_message_handler(
        cmd_cancel, lambda msg: msg.text.lower() == "cancel", state="*"
    )
    dp.register_message_handler(
        cmd_cancel, lambda msg: msg.text.lower() == "отмена", state="*"
    )
    dp.register_message_handler(cmd_available, commands=["available"])
    dp.register_message_handler(
        cmd_available, lambda message: message.text.startswith("💲Available")
    )
    dp.register_message_handler(
        cmd_available, lambda message: message.text.startswith("💲Баланс")
    )
    dp.register_message_handler(undo_transaction, commands=["undo"])
