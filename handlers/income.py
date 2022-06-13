from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup
from gspread.exceptions import GSpreadException

import database
import records
from keyboards import user
from server import _
from sheet import Sheet

# TODO: Needs refactoring


class IncomeForm(StatesGroup):
    """
    This form is used for income record.
    """

    amount = State()
    category = State()
    account = State()
    description = State()


async def process_income(message: Message, state: FSMContext):
    """
    The handler is used to retrieve a record of income through a form.
    To add a record, the user must specify the record data in multiple messages.
    To add an entry with a single command, the /addinc handler is used
    """
    # Starting form filling
    await IncomeForm.amount.set()
    await message.answer(_('Specify an amount of income\nor type "cancel"'))

    # As the user enters the amount of income,
    # I send a query to the table to get expense categories,
    # income categories, today's date, and accounts.
    # This is done to minimize the number of requests
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))

    try:
        user_data = user_sheet.get_day_categories_accounts()
    except GSpreadException:
        await state.finish()
        await message.answer(
            _(
                "😳 Something went wrong...\n\n"
                "Please try again later.\n"
                "If it does not work again, check your table or add it again via /register. "
                "Maybe you have changed the table and I can no longer work with it"
            ),
            reply_markup=user.main_keyb(),
        )
        return

    # I put the data in the state.proxy(),
    # I have not found a better way to store the data,
    # preserving access to it from other handlers
    async with state.proxy() as data:
        data["sheet data"] = user_data


async def process_income_amount(message: Message, state: FSMContext):
    """
    This handler is used to get the income amount after calling the /income command
    """
    # Parsing amount
    parsed_amount = records.parse_income_amount(message.text)

    # If the user entered an unrecognizable amount,
    # stop filling out the form and send main keyboard
    if parsed_amount is None:
        await message.answer(
            _("❌ Cannot understand this amount...\nTry to add /income one more time!"),
            reply_markup=user.main_keyb(),
        )
        # Stop form
        await state.finish()
        return

    # Defining keyboard markup
    in_categories_markup = ReplyKeyboardMarkup()
    async with state.proxy() as data:
        # Write amount data to dictionary
        data["amount"] = parsed_amount
        # Adding buttons to markup from data get before
        in_category_list = data["sheet data"]["income categories"]
        in_categories_markup = user.two_row_keyb(in_category_list)

    # Go to the next step of form and send message
    await IncomeForm.next()
    await message.answer(
        _("Specify a category of income"),
        reply_markup=in_categories_markup,
    )


async def process_income_category(message: Message, state: FSMContext):
    """
    This handler is used to get the income category after calling the /income command
    """
    # Defining keyboard markup
    accounts_markup = ReplyKeyboardMarkup()
    async with state.proxy() as data:
        # Parsing income category
        data["category"] = records._parse_income_category(
            message.text, data["sheet data"]
        )

        # If category remains None, user entered wrong category
        # Stop from getting and show main keyboard
        if data["category"] == None:
            await message.answer(
                _(
                    "❌ This income category doesn't exist...\n"
                    "Try to add /income one more time!"
                ),
                reply_markup=user.main_keyb(),
            )
            # Finish form
            await state.finish()
            return

        # Adding buttons to markup from data get before
        account_list = data["sheet data"]["accounts"]
        accounts_markup = user.two_row_keyb(account_list)

    # Go to the next step of the form
    await IncomeForm.next()
    # Send message with the buttons with accounts titles
    await message.answer(
        _("Specify an account"),
        reply_markup=accounts_markup,
    )


# --- END OF INCOME HANDLERS ---

# --- Next handlers are used both for Income and Expense comands
async def process_account(message: Message, state: FSMContext):
    """
    This handler is used to get the account after calling the /expense or /income command
    """
    async with state.proxy() as data:
        # Parsing account
        data["account"] = records._parse_account(message.text, data["sheet data"])

        # If account remains None, user entered wrong account
        # Stop from getting and show main keyboard
        if data["account"] == None:
            await message.answer(
                _("❌ This account doesn't exist...\nTry to add /income one more time!"),
                reply_markup=user.main_keyb(),
            )
            # Stop form
            await state.finish()
            return

    await IncomeForm.next()

    # Send a message with the button for cancelling description
    await message.answer(
        _("Specify a description"),
        reply_markup=user.no_description_keyb(),
    )


# --- Description handler used both in Income and Expense
async def process_record_description(message: Message, state: FSMContext):
    """
    This handler is used to get the expense or income description
    after calling the /expense or /income command.
    """
    record = []
    answer_message = _("👍 Successfully added {amount} to \n {cat} to {account}!")

    async with state.proxy() as data:
        # If not negative answer, add description to form
        data["description"] = ""
        if message.text not in ["No description", "Без описания"]:
            data["description"] = message.text

        # Creating list with expense or income data
        record = [
            data["sheet data"]["today"],
            data["description"],
            data["category"],
            data["amount"],
            data["account"],
        ]

        # Enter data to transactions list
        user_sheet = Sheet(database.get_sheet_id(message.from_user.id))

        try:
            user_sheet.add_record(record)
        except GSpreadException:
            await state.finish()
            await message.answer(
                _(
                    "😳 Something went wrong...\n\n"
                    "Please try again later.\n"
                    "If it does not work again, check your table or add it again via /register. "
                    "Maybe you have changed the table and I can no longer work with it"
                ),
                reply_markup=user.main_keyb(),
            )
            return

        # Send finish message and show main keyboard
        await message.answer(
            answer_message.format(
                amount=data["amount"], cat=data["category"], account=data["account"]
            ),
            reply_markup=user.main_keyb(),
        )

    # Stop form filling
    await state.finish()


async def cmd_addinc(message: Message):
    """Add the record of new income from user to users sheet"""
    # If user just type command
    if message.text == "/addinc":
        await message.answer(
            _(
                "Income can be added by:\n"
                "    `/addinc amount, category, [account], [description]`\n"
                "where account and description are optional.\n\n"
                "Example:\n"
                "    `/addinc 1200, Salary, N26, First job`\n"
                "    `/addinc 20.20, Cashback, Revolut`"
            ),
            parse_mode="Markdown",
            reply_markup=user.main_keyb(),
        )
        return

    # Parsing income
    raw_income = message.text[7:].split(",")
    parsed_income = records.parse_record(
        raw_income, message.from_user.id, type="income"
    )

    # If not parsed, send help message
    if parsed_income == []:
        await message.answer(
            _(
                "Cannot understand this income!\n\n"
                "Income can be added by:\n"
                "    `/addinc amount, category, [account], [description]`\n"
                "where account and description are optional.\n\n"
                "Example:\n"
                "    `/addinc 1200, Salary, N26, First job`\n"
                "    `/addinc 20.20, Cashback, Revolut`"
            ),
            parse_mode="Markdown",
        )
        return

    # If wrong amount
    if parsed_income[3] == None:
        await message.answer(
            _("Cannot understand this income!\nLooks like amount is wrong!"),
            reply_markup=user.main_keyb(),
        )
        return
    # If wrong category
    if parsed_income[2] == None:
        await message.answer(
            _(
                "Cannot understand this income!\n"
                + "Looks like this income category doesn't exist!"
            ),
            reply_markup=user.main_keyb(),
        )
        return
    # If wrong account
    if parsed_income[4] == None:
        await message.answer(
            _(
                "Cannot understand this income!\n"
                + "Looks like this account doesn't exist!"
            ),
            reply_markup=user.main_keyb(),
        )
        return

    # If successful, openning sheet, checking
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))

    try:
        user_sheet.add_record(parsed_income)
    except GSpreadException:
        await message.answer(
            _(
                "😳 Something went wrong...\n\n"
                "Please try again later.\n"
                "If it does not work again, check your table or add it again via /register. "
                "Maybe you have changed the table and I can no longer work with it"
            ),
            reply_markup=user.main_keyb(),
        )
        return

    await message.answer(
        _(
            "👍 Successfully added {amount} to {category}!".format(
                amount=parsed_income[3], category=parsed_income[2]
            )
        )
    )


def register_income(dp: Dispatcher):
    dp.register_message_handler(
        cmd_addinc, lambda message: message.text.startswith("/addinc")
    )
    dp.register_message_handler(process_income, commands=["income"])
    dp.register_message_handler(
        process_income, lambda message: message.text.startswith("➕Income")
    )
    dp.register_message_handler(
        process_income, lambda message: message.text.startswith("➕Доход")
    )
    dp.register_message_handler(process_income_amount, state=IncomeForm.amount)
    dp.register_message_handler(process_income_category, state=IncomeForm.category)
    dp.register_message_handler(process_account, state=IncomeForm.account)
    dp.register_message_handler(
        process_record_description, state=IncomeForm.description
    )
