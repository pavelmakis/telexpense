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


class ExpenseForm(StatesGroup):
    """
    This form is used for expense record.
    """

    amount = State()
    category = State()
    account = State()
    description = State()


async def process_expense(message: Message, state: FSMContext):
    """
    The handler is used to retrieve a record of expense through a form.
    To add a record, the user must specify the record data in multiple messages.
    To add an entry with a single command, the /addexp handler is used
    """
    # Starting form filling
    await ExpenseForm.amount.set()
    await message.answer(_('Specify an amount of expense\nor type "cancel"'))

    # As the user enters the amount of spending,
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
                "😳 Sorry, I cannot understand this format.\n\n"
                "Change something and try /currency again later"
            ),
            reply_markup=user.main_keyb(),
        )
        return

    # I put the data in the state.proxy(),
    # I have not found a better way to store the data,
    # preserving access to it from other handlers
    async with state.proxy() as data:
        data["sheet data"] = user_data


async def process_expense_amount(message: Message, state: FSMContext):
    """
    This handler is used to get the expense amount after calling the /expense command
    """
    # Parsing amount
    parsed_amount = records.parse_outcome_amount(message.text)

    # If the user entered an unrecognizable amount,
    # stop filling out the form and send main keyboard
    if parsed_amount is None:
        await message.answer(
            _("❌ Cannot understand this amount...\nTry to add /expense one more time!"),
            reply_markup=user.main_keyb(),
        )

        # Stop form
        await state.finish()
        return

    # Defining keyboard markup
    out_categories_markup = ReplyKeyboardMarkup()
    async with state.proxy() as data:
        # Write amount data to dictionary
        data["amount"] = parsed_amount

        # Getting keyboard markup from data get before
        out_category_list = data["sheet data"]["outcome categories"]
        out_categories_markup = user.two_row_keyb(out_category_list)

    # Go to the next step of form and send message
    await ExpenseForm.next()
    await message.answer(
        _("Specify a category of expense"),
        reply_markup=out_categories_markup,
    )


async def process_expense_category(message: Message, state: FSMContext):
    """
    This handler is used to get the expense category after calling the /expense command
    """
    # Defining keyboard markup
    accounts_markup = ReplyKeyboardMarkup()
    async with state.proxy() as data:
        # Parsing category
        data["category"] = records._parse_outcome_category(
            message.text, data["sheet data"]
        )

        # If category remains None, user entered wrong category
        # Stop from getting and show main keyboard
        if data["category"] == None:
            await message.answer(
                _(
                    "❌ This outcome category doesn't exist...\n"
                    "Try to add /expense one more time!"
                ),
                reply_markup=user.main_keyb(),
            )

            # Finish form
            await state.finish()
            return

        # Getting keyboard markup from data get before
        account_list = data["sheet data"]["accounts"]
        accounts_markup = user.two_row_keyb(account_list)

    # Go to the next step of the form
    await ExpenseForm.next()
    # Send message with the buttons with accounts titles
    await message.answer(
        # message.chat.id,
        _("Specify an account"),
        reply_markup=accounts_markup,
    )


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
                _(
                    "❌ This account doesn't exist...\nTry to add /expense one more time!"
                ),
                reply_markup=user.main_keyb(),
            )
            # Stop form
            await state.finish()
            return

    # This handler is used both for income and expense form
    # Go to the next step depending on which form is now working
    # current_state = await state.get_state()
    # if "IncomeForm" in current_state:
    #     await IncomeForm.next()
    # else:
    await ExpenseForm.next()
    # Send a message with the button for cancelling description
    await message.answer(
        # message.chat.id,
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
    async with state.proxy() as data:
        # If not negative answer, add description to form
        data["description"] = ""
        if message.text != "No description" or "Без описания":
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
                    "😳 Sorry, I cannot understand this format.\n\n"
                    "Change something and try /currency again later"
                ),
                reply_markup=user.main_keyb(),
            )
            return

        # Send finish message and show main keyboard
        answer_message = _(
            "👍 Successfully added {amount} to \n{cat} from {account}!".format(
                amount=data["amount"], cat=data["category"], account=data["account"]
            )
        )
        await message.answer(answer_message, reply_markup=user.main_keyb())

    # Stop form filling
    await state.finish()


async def cmd_addexp(message: Message):
    """Add the record of new expense from user to users sheet"""
    # If user just type command
    if message.text == "/addexp":
        await message.answer(
            _(
                "Expense can be added by:\n"
                "    `/addexp amount, category, [account], [description]`\n"
                "where account and description are optional.\n\n"
                "Example:\n"
                "    `/addexp 3.45, taxi, Revolut, From work`\n"
                "    `/addexp 9.87, Groceries, N26`"
            ),
            parse_mode="Markdown",
            reply_markup=user.main_keyb(),
        )
        return

    # Parsing expense
    raw_expense = message.text[7:].split(",")
    parsed_expense = records.parse_record(
        raw_expense, message.from_user.id, type="outcome"
    )

    # If not parsed, send help message
    if parsed_expense == []:
        await message.answer(
            _(
                "Cannot understand this expense!\n\n"
                "Expense can be added by:\n"
                "    `/addexp amount, category, [account], [description]`\n"
                "where account and description are optional.\n\n"
                "Example:\n"
                "    `/addexp 3.45, taxi, Revolut, From work`\n"
                "    `/addexp 9.87, Groceries, N26`"
            ),
            parse_mode="Markdown",
            reply_markup=user.main_keyb(),
        )
        return
    # If wrong amount
    if parsed_expense[3] == None:
        await message.answer(
            _("Cannot understand this expense!\nLooks like amount is wrong!"),
            reply_markup=user.main_keyb(),
        )
        return
    # If wrong category
    if parsed_expense[2] == None:
        await message.answer(
            _(
                "Cannot understand this expense!\n"
                "Looks like this category doesn't exist!"
            ),
            reply_markup=user.main_keyb(),
        )
        return
    # If wrong account
    if parsed_expense[4] == None:
        await message.answer(
            _(
                "Cannot understand this expense!\n"
                "Looks like this account doesn't exist!"
            ),
            reply_markup=user.main_keyb(),
        )
        return

    # If successful, openning cheet, checking
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))

    try:
        user_sheet.add_record(parsed_expense)
    except GSpreadException:
        await message.answer(
            _(
                "😳 Sorry, I cannot understand this format.\n\n"
                "Change something and try /currency again later"
            ),
            reply_markup=user.main_keyb(),
        )
        return

    await message.answer(
        _(
            "👍 Successfully added {amount} to {category}!".format(
                amount=parsed_expense[3], category=parsed_expense[2]
            )
        )
    )


def register_expenses(dp: Dispatcher):
    dp.register_message_handler(
        cmd_addexp, lambda message: message.text.startswith("/addexp")
    )
    dp.register_message_handler(process_expense, commands=["expense"])
    dp.register_message_handler(
        process_expense,
        lambda message: message.text.startswith("➖Expense"),
    )
    dp.register_message_handler(
        process_expense, lambda message: message.text.startswith("➖Расход")
    )
    dp.register_message_handler(process_expense_amount, state=ExpenseForm.amount)
    dp.register_message_handler(process_expense_category, state=ExpenseForm.category)
    dp.register_message_handler(process_account, state=ExpenseForm.account)
    dp.register_message_handler(
        process_record_description, state=ExpenseForm.description
    )
