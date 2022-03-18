import os
import logging
import sheet
import records
import answers
import keyboards

from aiogram import Bot, Dispatcher, executor, types
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
    if parsed_expense[2] == None:
        await message.answer(
            "Cannot understand this expense!\n"
            "Looks like amount is wrong!")
        return
    # If wrong category
    if parsed_expense[1] == None:
        await message.answer(
            "Cannot understand this expense!\n"
            "Looks like this category doesn't exist!")
        return
    # If wrong account
    if parsed_expense[3] == None:
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
    if parsed_income[2] == None:
        await message.answer(
            "Cannot understand this income!\n"
            "Looks like amount is wrong!")
        return
    # If wrong category
    if parsed_income[1] == None:
        await message.answer(
            "Cannot understand this income!\n"
            "Looks like this income category doesn't exist!")
        return
    # If wrong account
    if parsed_income[3] == None:
        await message.answer(
            "Cannot understand this income!\n"
            "Looks like this account doesn't exist!")
        return

    # If successful
    user_sheet = sheet.Sheet()
    user_sheet.add_record(parsed_income)
    await message.answer(f"Successfully added {parsed_income[3]} to " +
                         f"{parsed_income[2]}!", parse_mode='Markdown')
    

# --- /EXPENSE FORM HANDLERS ---
@dp.message_handler(commands=['expense'])
async def process_expense(message: types.Message):
    """
    The handler is used to retrieve a record of expense through a form. 
    To add a record, the user must specify the record data in multiple messages. 
    To add an entry with a single command, the /addexp handler is used
    """
    await RecordForm.amount.set()
    await bot.send_message(
            message.chat.id,
            "Specify an amount of expense")

@dp.message_handler(state=RecordForm.amount)
async def process_expense_amount(message: types.Message, state: FSMContext):
    """
    This handler is used to get the expense amount after calling the /expense command
    """
    # Parsing amount
    parsed_amount = records._parse_outcome_amount(message.text)

    # If not parsed, stop form getting
    # and show main keyboard
    if parsed_amount is None:
        await bot.send_message(
            message.chat.id,
            "Cannot understand this amount...\n"
            "Try to add /expense one more time!",
            reply_markup=keyboards.get_main_markup())
        await state.finish()
        return

    # Write amount data to dictionary
    async with state.proxy() as data:
        data['amount'] = parsed_amount

    # Go to the next step of form and send message
    await RecordForm.next()
    await bot.send_message(
            message.chat.id,
            "Specify a category of expense",
            reply_markup=keyboards.get_outcome_categories_markup())

@dp.message_handler(state=RecordForm.category)
async def process_expense_category(message: types.Message, state: FSMContext):
    """
    This handler is used to get the expense category after calling the /expense command
    """
    # Parsing expense category 
    user_sheet = sheet.Sheet()
    parsed_category = records._parse_outcome_category(message.text, user_sheet)

    # If not parsed, stop form getting
    # and show main keyboard
    if parsed_category is None:
        await bot.send_message(
            message.chat.id,
            "This outcome category doesn't exist...\n"
            "Try to add /expense one more time!",
            reply_markup=keyboards.get_main_markup())
        await state.finish()
        return

    # Write expense category to dictionary
    async with state.proxy() as data:
        data['category'] = parsed_category

    # Go to the next step of the form and send a message 
    # with the buttons with accounts titles
    await RecordForm.next()
    await bot.send_message(
            message.chat.id,
            "Specify an account of expense",
            reply_markup=keyboards.get_accounts_markup())

@dp.message_handler(state=RecordForm.account)
async def process_expense_account(message: types.Message, state: FSMContext):
    """
    This handler is used to get the expense account after calling the /expense command
    """
    user_sheet = sheet.Sheet()
    parsed_account = records._parse_account(message.text, user_sheet)

    # If not parsed, stop form getting and show main keyboard
    if parsed_account is None:
        await bot.send_message(
            message.chat.id,
            "This account doesn't exist...\n"
            "Try to add /expense one more time!",
            reply_markup=keyboards.get_main_markup())
        await state.finish()
        return

    # Write account to dictionary
    async with state.proxy() as data:
        data['account'] = parsed_account

    # Send finish message and show main keyboard
    await bot.send_message(
        message.chat.id,
        f"Successfully added {data['amount']} to {data['category']} from {data['account']}!",
        parse_mode='Markdown',
        reply_markup=keyboards.get_main_markup())

    # Stop form filling
    await state.finish()
# --- END OF /EXPENSE FORM HANDLERS ---

# --- /INCOME FORM HANDLERS ---





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)