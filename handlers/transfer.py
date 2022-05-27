from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup

import answers
import database
import keyboards
import records
from sheet import Sheet


class TransferForm(StatesGroup):
    """
    This form is used for transfer record
    """

    outcome_amount = State()
    outcome_account = State()
    income_amount = State()
    income_account = State()


async def process_transaction(message: Message, state: FSMContext):
    """
    The handler is used to retrieve a record of transfer through a form.
    To add a record, the user must specify the record data in multiple messages.
    To add an entry with a single command, the /addtran handler is used
    """

    # Starting form filling
    await TransferForm.outcome_amount.set()
    await message.answer('Specify an amount of transfer\nor type "cancel"')

    # As the user enters the amount of transfer,
    # I send a query to the table to get today date and accounts
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    if user_sheet == None:
        await message.answer(
            answers.error_message, reply_markup=keyboards.get_main_markup()
        )
        await state.finish()
        return
    user_data = user_sheet.get_day_accounts()

    # I put the data in the state.proxy(),
    # I have not found a better way to store the data,
    # preserving access to it from other handlers
    async with state.proxy() as data:
        data["today"] = user_data["today"]
        data["accounts"] = user_data["accounts"]


async def process_tran_outcome_amount(message: Message, state: FSMContext):
    """
    This handler is used to get the transfer outcome amount after
    calling the /transfer command
    """
    # Parsing amount
    parsed_amount = records.parse_outcome_amount(message.text)

    # If the user entered an unrecognizable amount,
    # stop filling out the form and send main keyboard
    if parsed_amount is None:
        await message.answer(
            "❌ Cannot understand this amount...\n"
            "Try to add /transfer one more time!",
            reply_markup=keyboards.get_main_markup(),
        )
        # Stop form
        await state.finish()
        return

    # Defining keyboard markup
    accounts_markup = ReplyKeyboardMarkup(
        resize_keyboard=True, selective=True, one_time_keyboard=True
    )
    async with state.proxy() as data:
        # Write amount data to dictionary
        data["outcome_amount"] = parsed_amount
        # Adding buttons to markup from data get before
        accounts_markup = keyboards.get_two_row_keyboard(data["accounts"])

    # Go to the next step of form and send message
    await TransferForm.next()
    await message.answer(
        "Specify the account from which\nthe money was transferred",
        reply_markup=accounts_markup,
    )


async def process_outcome_account(message: Message, state: FSMContext):
    """
    This handler is used to get the outcome account after calling /transfer
    """
    async with state.proxy() as data:
        # Parsing account
        parsed_account = records._parse_account(message.text, data)

        # If account is None, user entered wrong account
        # Stop from getting and show main keyboard
        if parsed_account == None:
            await message.answer(
                "❌ This account doesn't exist...\n"
                "Try to add /transfer one more time!",
                reply_markup=keyboards.get_main_markup(),
            )
            # Stop form
            await state.finish()
            return

        # If account isn't None, write account to form data
        data["outcome_account"] = parsed_account

    await TransferForm.next()
    # Send a message with the button for
    await message.answer(
        "Specify the amount added to the account to which the transfer was made.\n\n"
        + 'If the amounts are the same, tap "Same amount"',
        reply_markup=keyboards.get_same_amount_markup(),
    )


async def process_tran_income_amount(message: Message, state: FSMContext):
    """
    This handler is used to get the transfer income amount after
    calling the /transfer command
    """
    # Defining keyboard markup
    accounts_markup = ReplyKeyboardMarkup()

    async with state.proxy() as data:
        # If amount is same
        if message.text == "Same amount":
            data["income_amount"] = records.parse_income_amount(
                str(data["outcome_amount"])
            )

        else:
            # Parsing amount
            parsed_amount = records.parse_income_amount(message.text)

            # If the user entered an unrecognizable amount,
            # stop filling out the form and send main keyboard
            if parsed_amount is None:
                await message.answer(
                    "❌ Cannot understand this amount...\n"
                    "Try to add /transfer one more time!",
                    reply_markup=keyboards.get_main_markup(),
                )
                # Stop form
                await state.finish()
                return

            # Adding parsed data to form data
            data["income_amount"] = parsed_amount

        # Forming two column markup from data get before
        accounts_markup = keyboards.get_two_row_keyboard(data["accounts"])

    # Go to the next step of form and send message
    await TransferForm.next()
    await message.answer(
        "Specify the account to which\nthe money was transferred",
        reply_markup=accounts_markup,
    )


async def process_income_account(message: Message, state: FSMContext):
    """
    This handler is used to get the income account after calling /transfer
    """
    transaction_record = []
    async with state.proxy() as data:
        # Parsing account
        parsed_account = records._parse_account(message.text, data)

        # If account is None, user entered wrong account
        # Stop from getting and show main keyboard
        if parsed_account == None:
            await message.answer(
                "❌ This account doesn't exist...\n"
                "Try to add /transfer one more time!",
                reply_markup=keyboards.get_main_markup(),
            )
            # Stop form
            await state.finish()
            return

        # If account isn't None, write account to form data
        data["income_account"] = parsed_account
        # Prepare transfer record
        transaction_record = [
            data["today"],
            data["outcome_amount"],
            data["outcome_account"],
            data["income_amount"],
            data["income_account"],
        ]

    # Stop form filling
    await state.finish()

    # Enter data to transactions list
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    if user_sheet == None:
        await message.answer(
            answers.error_message, reply_markup=keyboards.get_main_markup()
        )
        await state.finish()
        return
    user_sheet.add_transaction(transaction_record)

    # Send a message with the button for
    await message.answer(
        "👍 Successfully added transfer\n"
        + f"from {transaction_record[2]} to {transaction_record[4]}!",
        reply_markup=keyboards.get_main_markup(),
    )


async def cmd_addtran(message: Message):
    # If user just type command
    if message.text == "/addtran":
        await message.answer(
            answers.tran_help,
            parse_mode="MarkdownV2",
            reply_markup=keyboards.get_main_markup(),
        )
        return

    # Parsing transaction
    raw_transaction = message.text[8:].split(",")
    parsed_transaction = records.parse_transaction(
        raw_transaction, message.from_user.id
    )

    # If not parsed, send help message
    if parsed_transaction == []:
        await message.answer(answers.wrong_tran, parse_mode="MarkdownV2")
        return

    # If wrong outcome amount
    if parsed_transaction[1] == None:
        await message.answer(
            "Cannot understand this transaction!\n"
            + "Looks like outcome amount is wrong!"
        )
        return

    # If wrong account
    if parsed_transaction[2] == None:
        await message.answer(
            "Cannot understand this transaction!\n"
            + "Looks like this outcome account doesn't exist!"
        )
        return

    # If wrong account
    if parsed_transaction[3] == None:
        await message.answer(
            "Cannot understand this transaction!\n"
            + "Looks like income amount is wrong!"
        )
        return

    # If wrong account
    if parsed_transaction[4] == None:
        await message.answer(
            "Cannot understand this transaction!\n"
            + "Looks like this income account doesn't exist!"
        )
        return

    # If success
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    if user_sheet == None:
        await message.answer(
            answers.error_message, reply_markup=keyboards.get_main_markup()
        )
        return

    user_sheet.add_transaction(parsed_transaction)
    await message.answer(
        "👍 Successfully added transaction from \n"
        + f"{parsed_transaction[2]} to {parsed_transaction[4]}!"
    )


def register_transfer(dp: Dispatcher):
    dp.register_message_handler(
        cmd_addtran, lambda message: message.text.startswith("/addtran")
    )
    dp.register_message_handler(process_transaction, commands=["transfer"])
    dp.register_message_handler(
        process_transaction, lambda message: message.text.startswith("💱Transfer")
    )
    dp.register_message_handler(
        process_tran_outcome_amount, state=TransferForm.outcome_amount
    )
    dp.register_message_handler(
        process_outcome_account, state=TransferForm.outcome_account
    )
    dp.register_message_handler(
        process_tran_income_amount, state=TransferForm.income_amount
    )
    dp.register_message_handler(
        process_income_account, state=TransferForm.income_account
    )
