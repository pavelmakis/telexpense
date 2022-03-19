from calendar import c
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


class RecordForm(StatesGroup):
    """
    This form is used both for expense and income.
    """
    amount = State()
    category = State()
    account = State()
    description = State()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply(f"Привет!",reply_markup=keyboards.greet_kb)

@dp.message_handler(commands=['available'])
async def send_total(message: types.Message):
    """Send an available amount of money from users sheet"""
    user_sheet = sheet.Sheet()
    available_amount = user_sheet.get_available()
    await message.answer(f"Сейчас доступно: {available_amount} на всех счетах")

@dp.message_handler(commands=['savings'])
async def send_savings(message: types.Message):
    """Send an amount of savings from users sheet"""
    user_sheet = sheet.Sheet()
    savings_amount = user_sheet.get_savings()
    await message.answer(f"У вас сбережений: {savings_amount}")

@dp.message_handler(commands=['total'])
async def send_total(message: types.Message):
    """Send a total amount of money from users sheet"""
    user_sheet = sheet.Sheet()
    total_amount = user_sheet.get_total()
    await message.answer(f"Всего денег: {total_amount} на всех счетах")

@dp.message_handler(lambda message: message.text.startswith('/addexp'))
async def send_total(message: types.Message):
    """Add the record of new expense from user to users sheet"""
    # Parsing expense
    raw_expense = message.text[7:].split(',')
    parsed_expense = records.parse_record(raw_expense, type='outcome')

    # If not parsed, send help message
    if parsed_expense == []:
        await message.answer(answers.WRONG_EXPENSE, parse_mode='Markdown')
        return
    # If wrong amount
    if parsed_expense[3] == None:
        await message.answer(
            "Cannot understand this expense!\n"
            "Looks like amount is wrong!")
        return
    # If wrong category
    if parsed_expense[2] == None:
        await message.answer(
            "Cannot understand this expense!\n"
            "Looks like this category doesn't exist!")
        return
    # If wrong account
    if parsed_expense[4] == None:
        await message.answer(
            "Cannot understand this expense!\n"
            "Looks like this account doesn't exist!")
        return

    # If successful
    user_sheet = sheet.Sheet()
    user_sheet.add_record(parsed_expense)
    await message.answer(f"Successfully added {parsed_expense[3]} to "
                         f"{parsed_expense[2]}!", parse_mode='Markdown')

@dp.message_handler(lambda message: message.text.startswith('/addinc'))
async def send_total(message: types.Message):
    """Add the record of new income from user to users sheet"""
    # Parsing income
    raw_income = message.text[7:].split(',')
    parsed_income = records.parse_record(raw_income, type='income')

    # If not parsed, send help message
    # TODO: Add message for wrong income
    if parsed_income == []:
        await message.answer(answers.WRONG_EXPENSE, parse_mode='Markdown')
        return
    # If wrong amount
    if parsed_income[3] == None:
        await message.answer(
            "Cannot understand this income!\n"
            "Looks like amount is wrong!")
        return
    # If wrong category
    if parsed_income[2] == None:
        await message.answer(
            "Cannot understand this income!\n"
            "Looks like this income category doesn't exist!")
        return
    # If wrong account
    if parsed_income[4] == None:
        await message.answer(
            "Cannot understand this income!\n"
            "Looks like this account doesn't exist!")
        return

    # If successful
    user_sheet = sheet.Sheet()
    user_sheet.add_record(parsed_income)
    await message.answer(f"Successfully added {parsed_income[3]} to " +
                         f"{parsed_income[2]}!")
    

# --- HADLER FOR CANCELLING /EXPENSE OR /INCOME FORM ---
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
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

# --- /EXPENSE FORM HANDLERS ---
@dp.message_handler(commands=['expense'])
async def process_expense(message: types.Message, state: FSMContext):
    """
    The handler is used to retrieve a record of expense through a form. 
    To add a record, the user must specify the record data in multiple messages. 
    To add an entry with a single command, the /addexp handler is used
    """
    # Starting form filling
    await RecordForm.amount.set()
    await bot.send_message(
            message.chat.id,
            "Specify an amount of expense")

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

@dp.message_handler(state=RecordForm.amount)
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
            "Cannot understand this amount...\n"
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
    await RecordForm.next()
    await bot.send_message(
            message.chat.id,
            "Specify a category of expense",
            reply_markup=out_categories_markup)

@dp.message_handler(state=RecordForm.category)
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
                "This outcome category doesn't exist...\n"
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
    await RecordForm.next()
    # Send message with the buttons with accounts titles
    await bot.send_message(
            message.chat.id,
            "Specify an account of expense",
            reply_markup=accounts_markup)

@dp.message_handler(state=RecordForm.account)
async def process_expense_account(message: types.Message, state: FSMContext):
    """
    This handler is used to get the expense account after calling the /expense command
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
                "This account doesn't exist...\n"
                "Try to add /expense one more time!",
                reply_markup=keyboards.get_main_markup())
            # Stop form
            await state.finish()
            return

    # Go to the next step of the form and send a message 
    # with the button for cancelling description
    await RecordForm.next()
    await bot.send_message(
        message.chat.id,
        "Specify a description of expense",
        reply_markup=keyboards.get_description_markup())

# --- END OF /EXPENSE FORM HANDLERS ---

# --- /INCOME FORM HANDLERS ---

# --- END OF /INCOME HANDLERS ---

# DESCRIPTION HANDLER
@dp.message_handler(state=RecordForm.description)
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
        await bot.send_message(
            message.chat.id,
            f"✅ Successfully added {data['amount']} to \n {data['category']} on {data['account']}!",
            reply_markup=keyboards.get_main_markup())

    # Stop form filling
    await state.finish()

    # Enter data to transactions list 
    user_sheet = sheet.Sheet()
    user_sheet.add_record(record)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)