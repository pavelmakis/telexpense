import os
import logging
import sheet
import records
import answers
import keyboards
import forms

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage


API_TOKEN = os.getenv('TELEXPENSE_TOKEN')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


dp.register_message_handler(forms.cancel_handler, commands=['cancel'], state="*")
dp.register_message_handler(forms.cancel_handler, lambda msg: msg.text.lower() == 'cancel', state="*")

dp.register_message_handler(forms.process_expense, commands=['expense'])
dp.register_message_handler(forms.process_expense_amount, state=forms.ExpenseForm.amount)
dp.register_message_handler(forms.process_expense_category, state=forms.ExpenseForm.category)
dp.register_message_handler(forms.process_account, state=forms.ExpenseForm.account)
dp.register_message_handler(forms.process_record_description, state=forms.ExpenseForm.description)

dp.register_message_handler(forms.process_income, commands=['income'])
dp.register_message_handler(forms.process_income_amount, state=forms.IncomeForm.amount)
dp.register_message_handler(forms.process_income_category, state=forms.IncomeForm.category)
dp.register_message_handler(forms.process_account, state=forms.IncomeForm.account)
dp.register_message_handler(forms.process_record_description, state=forms.IncomeForm.description)

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
    account_amounts = user_sheet.get_account_amounts()
    available = ""
    for i in range(len(account_amounts)):
        available += account_amounts[i][0]
        available += "   "
        available += account_amounts[i][1]
        available += '\n'
    await message.answer(f"Длина строки: {len(available)}")
    await message.answer(available)

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
    await message.answer(f"✅ Successfully added {parsed_expense[3]} to "
                         f"{parsed_expense[2]}!")

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
    await message.answer(f"✅ Successfully added {parsed_income[3]} to " +
                         f"{parsed_income[2]}!")
    


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)