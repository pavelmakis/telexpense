import os
import logging
import sheet
import records
import answers

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.getenv('TELEXPENSE_TOKEN')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply(f"Привет!")

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
    raw_transaction = message.text[7:].split(',')

    # Checking if command contains only one argument
    if len(raw_transaction) == 1:
        await message.answer(answers.WRONG_EXPENSE, parse_mode='Markdown')
        return
    
    # Parsing expense
    parsed_transaction = records.parse_transaction(raw_transaction)

    # If not parsed, send help message
    if parsed_transaction == []:
        await message.answer(answers.WRONG_EXPENSE, parse_mode='Markdown')
        return
    # If wrong amount
    if parsed_transaction[2] == None:
        await message.answer("Cannot understand this expense!\nLooks like amount is wrong!")
        return
    # If wrong category
    if parsed_transaction[1] == None:
        await message.answer("Cannot understand this expense!\n"
                            "Looks like this category doesn't exist!")
        return
    # If wrong account
    if parsed_transaction[3] == None:
        await message.answer("Cannot understand this expense!\n"
                            "Looks like this account doesn't exist!")
        return

    # If successful
    user_sheet = sheet.Sheet()
    user_sheet.add_record(parsed_transaction)
    await message.answer(f"Successfully added {parsed_transaction[2]} to "
                         "{parsed_transaction[1]}!", parse_mode='Markdown')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)