"""
This file contains aiogram handlers for user registration.
When user registers into bot, his Google sheet URL is added to database.
"""
import os
import logging
import database
import keyboards

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


class URLForm(StatesGroup):
    """
    This form is used for URL getter form.
    """
    url = State()

async def start_registering(message: types.Message, state: FSMContext):
    """
    This handler is used to ask user his sheet URL
    """
    # Starting form filling
    await URLForm.url.set()
    await bot.send_message(
        message.chat.id,
        'Send me the URL to your table')
    
async def process_url(message: types.Message, state: FSMContext):
    """
    This handler is used to check and add users URL to database.
    """
    async with state.proxy() as data:
        # Write data to dictionary
        database.insert_sheet_url(message.from_user.id, message.text)

    await bot.send_message(
        message.chat.id,
        'Added!',
        reply_markup=keyboards.get_main_markup())
    
    # Stop form
    await state.finish()
    