"""
This file contoins aiogram handlers for Income, Expense and Transaction commands
which are used to add records as a from. To add record in one command, /addinc, /addexp
and /addtran are used.    
"""
import os
import logging
import sheet
import records
import answers
import keyboards

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
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
    This form is used both for expense and income.
    """
    amount = State()
    category = State()
    account = State()
    description = State()


class IncomeForm(StatesGroup):
    """
    This form is used both for income.
    """
    amount = State()
    category = State()
    account = State()
    description = State()


async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel expense or income form filling
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await bot.send_message(
        message.chat.id,
        'Cancelled',
        reply_markup=keyboards.get_main_markup())

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
            'Specify an amount of expense or type "cancel"',
            reply_markup=keyboards.get_cancel_markup())

    # As the user enters the amount of spending,
    # I send a query to the table to get expense categories, 
    # income categories, today's date, and accounts.
    # This is done to minimize the number of requests
    user_sheet = sheet.Sheet()
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
    out_categories_markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                      selective=True,
                                                      one_time_keyboard=True)
    async with state.proxy() as data:
        # Write amount data to dictionary
        data['amount'] = parsed_amount
        # Adding buttons to markup from data get before
        out_category_list = data['sheet data']['outcome categories']
        for i in range(0, len(out_category_list), 2):
            # If there is only one item left...
            if len(out_category_list) - i == 1:
                # Adding last category as big button
                out_categories_markup.add(out_category_list[-1])
                break
            # Adding categories as two buttons in a row
            out_categories_markup.add(out_category_list[i], out_category_list[i+1])

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
    accounts_markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                      selective=True,
                                                      one_time_keyboard=True)
    async with state.proxy() as data:
        # Getting outcome categories from sheet data in state.proxy()
        category_list = data['sheet data']['outcome categories']
        # Setting category to None
        data['category'] = None
        for i in range(len(category_list)):
            # If user entered category is similar to data from sheet
            if message.text.lower() == category_list[i].lower():
                data['category'] = category_list[i]
                break
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

        # Adding buttons to markup from data get before
        account_list = data['sheet data']['accounts']
        for i in range(0, len(account_list), 2):
            # If there is only one item left...
            if len(account_list) - i == 1:
                # Adding last account as big button
                accounts_markup.add(account_list[-1])
                break
            # Adding accounts as two buttons in a row
            accounts_markup.add(account_list[i], account_list[i+1])

    # Go to the next step of the form
    await ExpenseForm.next()
    # Send message with the buttons with accounts titles
    await bot.send_message(
            message.chat.id,
            "Specify an account",
            reply_markup=accounts_markup)


async def process_account(message: types.Message, state: FSMContext):
    """
    This handler is used to get the account after calling the /expense or /income command
    """
    async with state.proxy() as data:
        # Getting accounts from sheet data in state.proxy()
        account_list = data['sheet data']['accounts']
        # Setting account to None
        data['account'] = None
        for i in range(len(account_list)):
            if message.text.lower() == account_list[i].lower():
                data['account'] = account_list[i]
                break
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
            'Specify an amount of income or type "cancel"',
            reply_markup=keyboards.get_cancel_markup())

    # As the user enters the amount of income,
    # I send a query to the table to get expense categories, 
    # income categories, today's date, and accounts.
    # This is done to minimize the number of requests
    user_sheet = sheet.Sheet()
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
    in_categories_markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                      selective=True,
                                                      one_time_keyboard=True)
    async with state.proxy() as data:
        # Write amount data to dictionary
        data['amount'] = parsed_amount
        # Adding buttons to markup from data get before
        in_category_list = data['sheet data']['income categories']
        for i in range(0, len(in_category_list), 2):
            # If there is only one item left...
            if len(in_category_list) - i == 1:
                # Adding last category as big button
                in_categories_markup.add(in_category_list[-1])
                break
            # Adding categories as two buttons in a row
            in_categories_markup.add(in_category_list[i], in_category_list[i+1])

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
    accounts_markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                      selective=True,
                                                      one_time_keyboard=True)
    async with state.proxy() as data:
        # Getting outcome categories from sheet data in state.proxy()
        category_list = data['sheet data']['income categories']
        # Setting category to None
        data['category'] = None
        for i in range(len(category_list)):
            # If user entered category is similar to data from sheet
            if message.text.lower() == category_list[i].lower():
                data['category'] = category_list[i]
                break
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
        for i in range(0, len(account_list), 2):
            # If there is only one item left...
            if len(account_list) - i == 1:
                # Adding last account as big button
                accounts_markup.add(account_list[-1])
                break
            # Adding accounts as two buttons in a row
            accounts_markup.add(account_list[i], account_list[i+1])
    
    # Go to the next step of the form
    await IncomeForm.next()
    # Send message with the buttons with accounts titles
    await bot.send_message(
            message.chat.id,
            "Specify an account",
            reply_markup=accounts_markup)

# --- END OF /INCOME HANDLERS ---

# --- HANDLERS WHICH ARE USED BOTH BY /INCOME AND /EXPENSE
# --- Account handler ----
#@dp.message_handler(state=IncomeForm.account)
#@dp.message_handler(state=ExpenseForm.account)
async def process_account(message: types.Message, state: FSMContext):
    """
    This handler is used to get the account after calling the /expense or /income command
    """
    async with state.proxy() as data:
        # Getting accounts from sheet data in state.proxy()
        account_list = data['sheet data']['accounts']
        # Setting account to None
        data['account'] = None
        for i in range(len(account_list)):
            if message.text.lower() == account_list[i].lower():
                data['account'] = account_list[i]
                break
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

# --- Description handler ---
#@dp.message_handler(state=IncomeForm.description)
#@dp.message_handler(state=ExpenseForm.description)
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
            answer_message = f"✅ Successfully added {data['amount']} to \n {data['category']} to {data['account']}!"
        else:
            answer_message = f"✅ Successfully added {data['amount']} to \n {data['category']} from {data['account']}!"
        await bot.send_message(
            message.chat.id,
            answer_message,
            reply_markup=keyboards.get_main_markup())

    # Stop form filling
    await state.finish()

    # Enter data to transactions list 
    # user_sheet = sheet.Sheet()
    # user_sheet.add_record(record)