from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup

import database
import keyboards
import messages
import records
from sheet import Sheet


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
    await message.answer(
        # message.chat.id,
        'Specify an amount of income\nor type "cancel"'
    )

    # As the user enters the amount of income,
    # I send a query to the table to get expense categories,
    # income categories, today's date, and accounts.
    # This is done to minimize the number of requests
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    if user_sheet == None:
        # await send_error_mes(message.chat.id)
        await message.answer(
            messages.error_message, reply_markup=keyboards.get_main_markup()
        )
        await state.finish()
        return
    user_data = user_sheet.get_day_categories_accounts()

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
            # message.chat.id,
            "❌ Cannot understand this amount...\n" "Try to add /income one more time!",
            reply_markup=keyboards.get_main_markup(),
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
        in_categories_markup = keyboards.get_two_row_keyboard(in_category_list)

    # Go to the next step of form and send message
    await IncomeForm.next()
    await message.answer(
        # message.chat.id,
        "Specify a category of income",
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
                # message.chat.id,
                "❌ This income category doesn't exist...\n"
                "Try to add /income one more time!",
                reply_markup=keyboards.get_main_markup(),
            )
            # Finish form
            await state.finish()
            return

        # Adding buttons to markup from data get before
        account_list = data["sheet data"]["accounts"]
        accounts_markup = keyboards.get_two_row_keyboard(account_list)

    # Go to the next step of the form
    await IncomeForm.next()
    # Send message with the buttons with accounts titles
    await message.answer(
        # message.chat.id,
        "Specify an account",
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
                # message.chat.id,
                "❌ This account doesn't exist...\n" "Try to add record one more time!",
                reply_markup=keyboards.get_main_markup(),
            )
            # Stop form
            await state.finish()
            return

    # This handler is used both for income and expense form
    # Go to the next step depending on which form is now working
    current_state = await state.get_state()
    # if "IncomeForm" in current_state:
    await IncomeForm.next()
    # else:
    #     await ExpenseForm.next()
    # Send a message with the button for cancelling description
    await message.answer(
        # message.chat.id,
        "Specify a description",
        reply_markup=keyboards.get_description_markup(),
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
        if message.text != "No description":
            data["description"] = message.text

        # Creating list with expense or income data
        record = [
            data["sheet data"]["today"],
            data["description"],
            data["category"],
            data["amount"],
            data["account"],
        ]

        # Send finish message and show main keyboard
        current_state = await state.get_state()
        answer_message = ""
        if "IncomeForm" in current_state:
            answer_message = f"👍 Successfully added {data['amount']} to \n {data['category']} to {data['account']}!"
        else:
            answer_message = f"👍 Successfully added {data['amount']} to \n {data['category']} from {data['account']}!"
        await message.answer(
            # message.chat.id,
            answer_message,
            reply_markup=keyboards.get_main_markup(),
        )

    # Stop form filling
    await state.finish()

    # Enter data to transactions list
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    if user_sheet == None:
        # await send_error_mes(message.chat.id)
        await message.answer(
            messages.error_message, reply_markup=keyboards.get_main_markup()
        )
        await state.finish()
        return

    user_sheet.add_record(record)


async def cmd_addinc(message: Message):
    """Add the record of new income from user to users sheet"""
    # If user just type command
    if message.text == "/addinc":
        await message.answer(
            messages.income_help,
            parse_mode="Markdown",
            reply_markup=keyboards.get_main_markup(),
        )
        return

    # Parsing income
    raw_income = message.text[7:].split(",")
    parsed_income = records.parse_record(
        raw_income, message.from_user.id, type="income"
    )

    # If not parsed, send help message
    if parsed_income == []:
        await message.answer(messages.wrong_income, parse_mode="Markdown")
        return
    # If wrong amount
    if parsed_income[3] == None:
        await message.answer(
            "Cannot understand this income!\n" + "Looks like amount is wrong!",
            reply_markup=keyboards.get_main_markup(),
        )
        return
    # If wrong category
    if parsed_income[2] == None:
        await message.answer(
            "Cannot understand this income!\n"
            + "Looks like this income category doesn't exist!",
            reply_markup=keyboards.get_main_markup(),
        )
        return
    # If wrong account
    if parsed_income[4] == None:
        await message.answer(
            "Cannot understand this income!\n"
            + "Looks like this account doesn't exist!",
            reply_markup=keyboards.get_main_markup(),
        )
        return

    # If successful, openning sheet, checking
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    if user_sheet == None:
        await message.answer(
            messages.error_message, reply_markup=keyboards.get_main_markup()
        )
        return

    user_sheet.add_record(parsed_income)
    await message.answer(
        f"👍 Successfully added {parsed_income[3]} to\n" + f"{parsed_income[2]}!"
    )


def register_income(dp: Dispatcher):
    dp.register_message_handler(
        cmd_addinc, lambda message: message.text.startswith("/addinc")
    )
    dp.register_message_handler(process_income, commands=["income"])
    dp.register_message_handler(
        process_income, lambda message: message.text.startswith("➕Income")
    )
    dp.register_message_handler(process_income_amount, state=IncomeForm.amount)
    dp.register_message_handler(process_income_category, state=IncomeForm.category)
    dp.register_message_handler(process_account, state=IncomeForm.account)
    dp.register_message_handler(
        process_record_description, state=IncomeForm.description
    )
