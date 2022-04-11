"""
This file contains aiogram handlers for Income, Expense and Transaction commands
which are used to add records as a from. To add record in one command, /addinc, /addexp
and /addtran are used.    
"""
import os
import logging
import records
import keyboards
import database
import answers
from sheet import Sheet

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


API_TOKEN = os.getenv('TELEXPENSE_TOKEN')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


class ExpenseForm(StatesGroup):
    """
    This form is used for expense record.
    """
    amount = State()
    category = State()
    account = State()
    description = State()


class IncomeForm(StatesGroup):
    """
    This form is used for income record.
    """
    amount = State()
    category = State()
    account = State()
    description = State()


class TransactionForm(StatesGroup):
    """
    This form is used for transaction record
    """
    outcome_amount = State()
    outcome_account = State()
    income_amount = State()
    income_account = State()


async def send_error_mes(chat_id):
    await bot.send_message(
        chat_id,
        answers.error_message,
        reply_markup=keyboards.get_main_markup())

# --- CANCEL HANDLER ---
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any form filling
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()
    # Show main screen keyboard
    await bot.send_message(
        message.chat.id,
        'Cancelled',
        reply_markup=keyboards.get_main_markup())

# --- START OF EXPENSE HANDLERS ---
async def process_expense(message: types.Message, state: FSMContext):
    """
    The handler is used to retrieve a record of expense through a form. 
    To add a record, the user must specify the record data in multiple messages. 
    To add an entry with a single command, the /addexp handler is used
    """
    # Starting form filling
    await ExpenseForm.amount.set()
    await bot.send_message(
            message.chat.id,
            'Specify an amount of expense\nor type "cancel"')

    # As the user enters the amount of spending,
    # I send a query to the table to get expense categories, 
    # income categories, today's date, and accounts.
    # This is done to minimize the number of requests
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    if user_sheet == None:
        await send_error_mes(message.chat.id)
        await state.finish()
        return
    user_data = user_sheet.get_day_categories_accounts()

    # I put the data in the state.proxy(),
    # I have not found a better way to store the data,
    # preserving access to it from other handlers
    async with state.proxy() as data:
        data['sheet data'] = user_data
    
async def process_expense_amount(message: types.Message, state: FSMContext):
    """
    This handler is used to get the expense amount after calling the /expense command
    """
    # Parsing amount
    parsed_amount = records.parse_outcome_amount(message.text)

    # If the user entered an unrecognizable amount,
    # stop filling out the form and send main keyboard
    if parsed_amount is None:
        await bot.send_message(
            message.chat.id,
            "❌ Cannot understand this amount...\n"
            "Try to add /expense one more time!",
            reply_markup=keyboards.get_main_markup())

        # Stop form
        await state.finish()
        return

    # Defining keyboard markup
    out_categories_markup = types.ReplyKeyboardMarkup()
    async with state.proxy() as data:
        # Write amount data to dictionary
        data['amount'] = parsed_amount

        # Getting keyboard markup from data get before
        out_category_list = data['sheet data']['outcome categories']
        out_categories_markup = keyboards.get_two_row_keyboard(out_category_list)

    # Go to the next step of form and send message
    await ExpenseForm.next()
    await bot.send_message(
            message.chat.id,
            "Specify a category of expense",
            reply_markup=out_categories_markup)

async def process_expense_category(message: types.Message, state: FSMContext):
    """
    This handler is used to get the expense category after calling the /expense command
    """
    # Defining keyboard markup
    accounts_markup = types.ReplyKeyboardMarkup()
    async with state.proxy() as data:
        # Parsing category
        data['category'] = records._parse_outcome_category(
            message.text, data['sheet data'])

        # If category remains None, user entered wrong category
        # Stop from getting and show main keyboard
        if data['category'] == None:
            await bot.send_message(
                message.chat.id,
                "❌ This outcome category doesn't exist...\n"
                "Try to add /expense one more time!",
                reply_markup=keyboards.get_main_markup())

            # Finish form
            await state.finish()
            return

        # Getting keyboard markup from data get before
        account_list = data['sheet data']['accounts']
        accounts_markup = keyboards.get_two_row_keyboard(account_list)

    # Go to the next step of the form
    await ExpenseForm.next()
    # Send message with the buttons with accounts titles
    await bot.send_message(
            message.chat.id,
            "Specify an account",
            reply_markup=accounts_markup)
# --- END OF EXPENSE HANDLERS ---

# --- START OF INCOME HABDLERS ---
async def process_income(message: types.Message, state: FSMContext):
    """
    The handler is used to retrieve a record of income through a form. 
    To add a record, the user must specify the record data in multiple messages. 
    To add an entry with a single command, the /addinc handler is used
    """
    # Starting form filling
    await IncomeForm.amount.set()
    await bot.send_message(
            message.chat.id,
            'Specify an amount of income\nor type "cancel"')

    # As the user enters the amount of income,
    # I send a query to the table to get expense categories, 
    # income categories, today's date, and accounts.
    # This is done to minimize the number of requests
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    if user_sheet == None:
        await send_error_mes(message.chat.id)
        await state.finish()
        return
    user_data = user_sheet.get_day_categories_accounts()

    # I put the data in the state.proxy(),
    # I have not found a better way to store the data,
    # preserving access to it from other handlers
    async with state.proxy() as data:
        data['sheet data'] = user_data

async def process_income_amount(message: types.Message, state: FSMContext):
    """
    This handler is used to get the income amount after calling the /income command
    """
    # Parsing amount
    parsed_amount = records.parse_income_amount(message.text)

    # If the user entered an unrecognizable amount,
    # stop filling out the form and send main keyboard
    if parsed_amount is None:
        await bot.send_message(
            message.chat.id,
            "❌ Cannot understand this amount...\n"
            "Try to add /income one more time!",
            reply_markup=keyboards.get_main_markup())
        # Stop form
        await state.finish()
        return
    
    # Defining keyboard markup
    in_categories_markup = types.ReplyKeyboardMarkup()
    async with state.proxy() as data:
        # Write amount data to dictionary
        data['amount'] = parsed_amount
        # Adding buttons to markup from data get before
        in_category_list = data['sheet data']['income categories']
        in_categories_markup = keyboards.get_two_row_keyboard(in_category_list)

    # Go to the next step of form and send message
    await IncomeForm.next()
    await bot.send_message(
            message.chat.id,
            "Specify a category of income",
            reply_markup=in_categories_markup)

async def process_income_category(message: types.Message, state: FSMContext):
    """
    This handler is used to get the income category after calling the /income command
    """
    # Defining keyboard markup
    accounts_markup = types.ReplyKeyboardMarkup()
    async with state.proxy() as data:
        # Parsing income category
        data['category'] = records._parse_income_category(
            message.text, data['sheet data'])

        # If category remains None, user entered wrong category
        # Stop from getting and show main keyboard
        if data['category'] == None:
            await bot.send_message(
                message.chat.id,
                "❌ This income category doesn't exist...\n"
                "Try to add /income one more time!",
                reply_markup=keyboards.get_main_markup())
            # Finish form
            await state.finish()
            return

        # Adding buttons to markup from data get before
        account_list = data['sheet data']['accounts']
        accounts_markup = keyboards.get_two_row_keyboard(account_list)
    
    # Go to the next step of the form
    await IncomeForm.next()
    # Send message with the buttons with accounts titles
    await bot.send_message(
            message.chat.id,
            "Specify an account",
            reply_markup=accounts_markup)
# --- END OF INCOME HANDLERS ---

# --- Next handlers are used both for Income and Expense comands
async def process_account(message: types.Message, state: FSMContext):
    """
    This handler is used to get the account after calling the /expense or /income command
    """
    async with state.proxy() as data:
        # Parsing account
        data['account'] = records._parse_account(
            message.text, data['sheet data'])

        # If account remains None, user entered wrong account
        # Stop from getting and show main keyboard
        if data['account'] == None:
            await bot.send_message(
                message.chat.id,
                "❌ This account doesn't exist...\n"
                "Try to add record one more time!",
                reply_markup=keyboards.get_main_markup())
            # Stop form
            await state.finish()
            return

    # This handler is used both for income and expense form
    # Go to the next step depending on which form is now working
    current_state = await state.get_state()
    if "IncomeForm" in current_state:
        await IncomeForm.next()
    else:
        await ExpenseForm.next()
    # Send a message with the button for cancelling description
    await bot.send_message(
        message.chat.id,
        "Specify a description",
        reply_markup=keyboards.get_description_markup())

# --- Description handler used both in Income and Expense
async def process_record_description(message: types.Message, state: FSMContext):
    """
    This handler is used to get the expense or income description
    after calling the /expense or /income command.
    """
    record = []
    async with state.proxy() as data:
        # If not negative answer, add description to form
        data['description'] = ""
        if message.text != "No description":
            data['description'] = message.text

        # Creating list with expense or income data
        record = [data['sheet data']['today'], data['description'], 
                  data['category'], data['amount'], data['account']]
        
        # Send finish message and show main keyboard
        current_state = await state.get_state()
        answer_message = ""
        if "IncomeForm" in current_state:
            answer_message = f"👍 Successfully added {data['amount']} to \n {data['category']} to {data['account']}!"
        else:
            answer_message = f"👍 Successfully added {data['amount']} to \n {data['category']} from {data['account']}!"
        await bot.send_message(
            message.chat.id,
            answer_message,
            reply_markup=keyboards.get_main_markup())

    # Stop form filling
    await state.finish()

    # Enter data to transactions list 
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    if user_sheet == None:
        await send_error_mes(message.chat.id)
        await state.finish()
        return

    user_sheet.add_record(record)

# --- START OF TRANSACTION HANDLERS ---
async def process_transaction(message: types.Message, state: FSMContext):
    """
    The handler is used to retrieve a record of transaction through a form. 
    To add a record, the user must specify the record data in multiple messages. 
    To add an entry with a single command, the /addtran handler is used
    """

    # Starting form filling
    await TransactionForm.outcome_amount.set()
    await bot.send_message(
            message.chat.id,
            'Specify an amount of transaction\nor type "cancel"')
    
    # As the user enters the amount of transaction,
    # I send a query to the table to get today date and accounts
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    if user_sheet == None:
        await send_error_mes(message.chat.id)
        await state.finish()
        return
    user_data = user_sheet.get_day_accounts()
    
    # I put the data in the state.proxy(),
    # I have not found a better way to store the data,
    # preserving access to it from other handlers
    async with state.proxy() as data:
        data['today'] = user_data['today']
        data['accounts'] = user_data['accounts']

async def process_tran_outcome_amount(message: types.Message, state: FSMContext):
    """
    This handler is used to get the transaction outcome amount after 
    calling the /transaction command
    """
    # Parsing amount
    parsed_amount = records.parse_outcome_amount(message.text)

    # If the user entered an unrecognizable amount,
    # stop filling out the form and send main keyboard
    if parsed_amount is None:
        await bot.send_message(
            message.chat.id,
            "❌ Cannot understand this amount...\n"
            "Try to add /transaction one more time!",
            reply_markup=keyboards.get_main_markup())
        # Stop form
        await state.finish()
        return

    # Defining keyboard markup
    accounts_markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                      selective=True,
                                                      one_time_keyboard=True)
    async with state.proxy() as data:
        # Write amount data to dictionary
        data['outcome_amount'] = parsed_amount
        # Adding buttons to markup from data get before
        accounts_markup = keyboards.get_two_row_keyboard(data['accounts'])

    # Go to the next step of form and send message
    await TransactionForm.next()
    await bot.send_message(
            message.chat.id,
            "Specify the account from which\nthe money was transferred",
            reply_markup=accounts_markup)

async def process_outcome_account(message: types.Message, state: FSMContext):
    """
    This handler is used to get the outcome account after calling /transaction
    """
    async with state.proxy() as data:
        # Parsing account
        parsed_account = records._parse_account(message.text, data)

        # If account is None, user entered wrong account
        # Stop from getting and show main keyboard
        if parsed_account == None:
            await bot.send_message(
                message.chat.id,
                "❌ This account doesn't exist...\n"
                "Try to add /transaction one more time!",
                reply_markup=keyboards.get_main_markup())
            # Stop form
            await state.finish()
            return

        # If account isn't None, write account to form data
        data['outcome_account'] = parsed_account

    await TransactionForm.next()
    # Send a message with the button for 
    await bot.send_message(
        message.chat.id,
        "Specify the amount added to the account to which the transfer was made.\n\n" +
        'If the amounts are the same, tap "Same amount"',
        reply_markup=keyboards.get_same_amount_markup())

async def process_tran_income_amount(message: types.Message, state: FSMContext):
    """
    This handler is used to get the transaction income amount after 
    calling the /transaction command
    """
    # Defining keyboard markup
    accounts_markup = types.ReplyKeyboardMarkup()

    async with state.proxy() as data:
        # If amount is same
        if message.text == "Same amount":
            data['income_amount'] = records.parse_income_amount(
                                        str(data['outcome_amount']))

        else:
            # Parsing amount
            parsed_amount = records.parse_income_amount(message.text)

            # If the user entered an unrecognizable amount,
            # stop filling out the form and send main keyboard
            if parsed_amount is None:
                await bot.send_message(
                    message.chat.id,
                    "❌ Cannot understand this amount...\n"
                    "Try to add /transaction one more time!",
                    reply_markup=keyboards.get_main_markup())
                # Stop form
                await state.finish()
                return
            
            # Adding parsed data to form data
            data['income_amount'] = parsed_amount
        
        # Forming two column markup from data get before
        accounts_markup = keyboards.get_two_row_keyboard(data['accounts'])

    # Go to the next step of form and send message
    await TransactionForm.next()
    await bot.send_message(
            message.chat.id,
            "Specify the account to which\nthe money was transferred",
            reply_markup=accounts_markup)

async def process_income_account(message: types.Message, state: FSMContext):
    """
    This handler is used to get the income account after calling /transaction
    """
    transaction_record = []
    async with state.proxy() as data:
        # Parsing account
        parsed_account = records._parse_account(message.text, data)

        # If account is None, user entered wrong account
        # Stop from getting and show main keyboard
        if parsed_account == None:
            await bot.send_message(
                message.chat.id,
                "❌ This account doesn't exist...\n"
                "Try to add /transaction one more time!",
                reply_markup=keyboards.get_main_markup())
            # Stop form
            await state.finish()
            return

        # If account isn't None, write account to form data
        data['income_account'] = parsed_account
        # Prepare transaction record
        transaction_record = [data['today'], data['outcome_amount'],
                              data['outcome_account'], 
                              data['income_amount'], data['income_account']]

    # Stop form filling
    await state.finish()

    # Enter data to transactions list 
    user_sheet = Sheet(database.get_sheet_id(message.from_user.id))
    if user_sheet == None:
        await send_error_mes(message.chat.id)
        await state.finish()
        return
    user_sheet.add_transaction(transaction_record)

    # Send a message with the button for 
    await bot.send_message(
        message.chat.id,
        "👍 Successfully added transaction\n" +
        f"from {transaction_record[2]} to {transaction_record[4]}!",
        reply_markup=keyboards.get_main_markup())
