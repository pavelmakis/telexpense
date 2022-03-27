import os
import logging
import sheet
import records
import answers
import keyboards
import forms
import database
import regist

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage


API_TOKEN = os.getenv('TELEXPENSE_TOKEN')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

unregistered = lambda message: not database.is_user_registered(message.from_user.id)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    await message.reply(f"Hi! I'm Telexpense bot. I can work with Google Sheet!",
                        reply_markup=keyboards.get_register_markup())

# Registering handlers for user registration
dp.register_message_handler(regist.start_registering, commands=['register'])
dp.register_message_handler(regist.process_url, state=regist.URLForm.url)

@dp.message_handler(unregistered, content_types=['any'])
async def handle_unregistered(message: types.Message):
    await bot.send_message(
        message.chat.id,
        "I can work only with registered users!\n"
        "Read the wiki or type /register",
        reply_markup=keyboards.get_register_markup())
    await bot.delete_message(message.chat.id, message.message_id)
    return

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    """
    This handler will be called when user sends /help command
    """
    await message.reply(answers.help,
                        parse_mode='Markdown',
                        reply_markup=keyboards.get_main_markup())

@dp.message_handler(commands=['cancel'])
@dp.message_handler(lambda msg: msg.text.lower() == 'cancel')
async def send_cancel_warning(message: types.Message):
    """Send a warning that /cancel works only if you are filling the form"""
    await bot.send_message(
        message.chat.id,
        "Can cancel only while you are filling a record form.\n\n" +
        "Nothing to cancel now!",
        reply_markup=keyboards.get_main_markup())

# Registering handler for form canceling
dp.register_message_handler(forms.cancel_handler, commands=['cancel'], state="*")
dp.register_message_handler(forms.cancel_handler, 
                            lambda msg: msg.text.lower() == 'cancel', state="*")



# Registering handlers for /expense form
dp.register_message_handler(forms.process_expense, commands=['expense'])
dp.register_message_handler(forms.process_expense, 
                            lambda message: message.text.startswith('➖Expense'))
dp.register_message_handler(forms.process_expense_amount, 
                            state=forms.ExpenseForm.amount)
dp.register_message_handler(forms.process_expense_category, 
                            state=forms.ExpenseForm.category)
dp.register_message_handler(forms.process_account, 
                            state=forms.ExpenseForm.account)
dp.register_message_handler(forms.process_record_description,
                            state=forms.ExpenseForm.description)

# Registering handlers for /income form
dp.register_message_handler(forms.process_income, 
                            commands=['income'])
dp.register_message_handler(forms.process_income, 
                            lambda message: message.text.startswith('➕Income'))
dp.register_message_handler(forms.process_income_amount, 
                            state=forms.IncomeForm.amount)
dp.register_message_handler(forms.process_income_category, 
                            state=forms.IncomeForm.category)
dp.register_message_handler(forms.process_account, 
                            state=forms.IncomeForm.account)
dp.register_message_handler(forms.process_record_description,
                            state=forms.IncomeForm.description)

# Registering handlers for /transaction form
dp.register_message_handler(forms.process_transaction, 
                            commands=['transaction'])
dp.register_message_handler(forms.process_transaction, 
                            lambda message: message.text.startswith('💱Transaction'))
dp.register_message_handler(forms.process_tran_outcome_amount, 
                            state=forms.TransactionForm.outcome_amount)
dp.register_message_handler(forms.process_outcome_account, 
                            state=forms.TransactionForm.outcome_account)
dp.register_message_handler(forms.process_tran_income_amount, 
                            state=forms.TransactionForm.income_amount)
dp.register_message_handler(forms.process_income_account, 
                            state=forms.TransactionForm.income_account)




@dp.message_handler(commands=['available'])
@dp.message_handler(lambda message: message.text.startswith('💲Available'))
async def send_total(message: types.Message):
    """Send a list of accounts and its amounts from users sheet"""
    user_sheet = sheet.Sheet()
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
    for i in range(len(amounts)):
        # Current line lenght
        text_lenght = len(amounts[i][0]) + len(amounts[i][1])
        available += amounts[i][0]
        # max_text_lenght + max_digit_lenght is the longest line
        # 2 (spaces) is the indent between account column and amount column
        available += " " * (max_text_lenght + max_digit_lenght - text_lenght + 2)
        available += amounts[i][1] + '\n'
    available += "```"

    await bot.send_message(
        message.chat.id, available,
        parse_mode='MarkdownV2',
        reply_markup=keyboards.get_main_markup())

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
async def add_exp(message: types.Message):
    """Add the record of new expense from user to users sheet"""
    # If user just type command
    if message.text == "/addexp":
        await bot.send_message(
            message.chat.id,
            answers.expense_help,
            parse_mode='Markdown',
            reply_markup=keyboards.get_main_markup())
        return

    # Parsing expense
    raw_expense = message.text[7:].split(',')
    parsed_expense = records.parse_record(raw_expense, type='outcome')

    # If not parsed, send help message
    if parsed_expense == []:
        await bot.send_message(
            message.chat.id,
            answers.wrong_expense, 
            parse_mode='Markdown',
            reply_markup=keyboards.get_main_markup())
        return
    # If wrong amount
    if parsed_expense[3] == None:
        await bot.send_message(
            message.chat.id,
            "Cannot understand this expense!\n" +
            "Looks like amount is wrong!",
            reply_markup=keyboards.get_main_markup())
        return
    # If wrong category
    if parsed_expense[2] == None:
        await bot.send_message(
            message.chat.id,
            "Cannot understand this expense!\n" +
            "Looks like this category doesn't exist!",
            reply_markup=keyboards.get_main_markup())
        return
    # If wrong account
    if parsed_expense[4] == None:
        await bot.send_message(
            message.chat.id,
            "Cannot understand this expense!\n" +
            "Looks like this account doesn't exist!",
            reply_markup=keyboards.get_main_markup())
        return

    # If successful
    user_sheet = sheet.Sheet()
    user_sheet.add_record(parsed_expense)
    await bot.send_message(
            message.chat.id,
            "👍 Successfully added " +
            f"{parsed_expense[3]} to\n"
            f"{parsed_expense[2]}!")

@dp.message_handler(lambda message: message.text.startswith('/addinc'))
async def add_inc(message: types.Message):
    """Add the record of new income from user to users sheet"""
    # If user just type command
    if message.text == "/addinc":
        await bot.send_message(
            message.chat.id,
            answers.income_help,
            parse_mode='Markdown',
            reply_markup=keyboards.get_main_markup())
        return

    # Parsing income
    raw_income = message.text[7:].split(',')
    parsed_income = records.parse_record(raw_income, type='income')

    # If not parsed, send help message
    if parsed_income == []:
        await bot.send_message(
            message.chat.id,
            answers.wrong_income, 
            parse_mode='Markdown')
        return
    # If wrong amount
    if parsed_income[3] == None:
        await bot.send_message(
            message.chat.id,
            "Cannot understand this income!\n" +
            "Looks like amount is wrong!",
            reply_markup=keyboards.get_main_markup())
        return
    # If wrong category
    if parsed_income[2] == None:
        await bot.send_message(
            message.chat.id,
            "Cannot understand this income!\n" +
            "Looks like this income category doesn't exist!",
            reply_markup=keyboards.get_main_markup())
        return
    # If wrong account
    if parsed_income[4] == None:
        await bot.send_message(
            message.chat.id,
            "Cannot understand this income!\n" +
            "Looks like this account doesn't exist!",
            reply_markup=keyboards.get_main_markup())
        return

    # If successful
    user_sheet = sheet.Sheet()
    user_sheet.add_record(parsed_income)
    await bot.send_message(
        message.chat.id,
        f"👍 Successfully added {parsed_income[3]} to\n" +
        f"{parsed_income[2]}!")

@dp.message_handler(lambda message: message.text.startswith('/addtran'))
async def add_tran(message: types.Message):
    # If user just type command
    if message.text == "/addtran":
        await bot.send_message(
            message.chat.id,
            answers.tran_help,
            parse_mode='MarkdownV2',
            reply_markup=keyboards.get_main_markup())
        return

    # Parsing transaction
    raw_transaction = message.text[8:].split(',')
    parsed_transaction = records.parse_transaction(raw_transaction)

    # If not parsed, send help message
    if parsed_transaction == []:
        await bot.send_message(
            message.chat.id, answers.wrong_tran, 
            parse_mode='MarkdownV2')
        return

    # If wrong outcome amount
    if parsed_transaction[1] == None:
        await bot.send_message(
            message.chat.id,
            "Cannot understand this transaction!\n" +
            "Looks like outcome amount is wrong!")
        return

    # If wrong account
    if parsed_transaction[2] == None:
        await bot.send_message(
            message.chat.id,
            "Cannot understand this transaction!\n" +
            "Looks like this outcome account doesn't exist!")
        return

    # If wrong account
    if parsed_transaction[3] == None:
        await bot.send_message(
            message.chat.id,
            "Cannot understand this transaction!\n" +
            "Looks like income amount is wrong!")
        return

    # If wrong account
    if parsed_transaction[4] == None:
        await bot.send_message(
            message.chat.id,
            "Cannot understand this transaction!\n" +
            "Looks like this income account doesn't exist!")
        return

    # If success
    user_sheet = sheet.Sheet()
    user_sheet.add_transaction(parsed_transaction)
    await bot.send_message(
        message.chat.id,
        "👍 Successfully added transaction from \n" +
        f"{parsed_transaction[2]} to {parsed_transaction[4]}!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)