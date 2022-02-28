import os
import logging
import sheet

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
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    user_sheet = sheet.Sheet()
    available_amount = user_sheet.get_available()
    await message.answer(f"Сейчас доступно: {available_amount} на всех счетах")

@dp.message_handler(commands=['savings'])
async def send_savings(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    user_sheet = sheet.Sheet()
    savings_amount = user_sheet.get_savings()
    await message.answer(f"У вас сбережений: {savings_amount}")

@dp.message_handler(commands=['total'])
async def send_total(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    user_sheet = sheet.Sheet()
    total_amount = user_sheet.get_total()
    await message.answer(f"Всего денег: {total_amount} на всех счетах")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)