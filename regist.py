"""
This file contains aiogram handlers for user registration.
When user registers into bot, his Google sheet URL is added to database.
"""
import os
import logging
import database
import keyboards
from sheet import Sheet

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from gspread import utils


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
    # If user is already registered
    if database.is_user_registered(message.from_user.id):
        await bot.send_message(
            message.chat.id,
            "I know you! You are alreafy registered!)")
        return

    # Starting form filling
    await URLForm.url.set()
    await bot.send_message(
        message.chat.id,
        "I can only work with one Google Spreadsheet template. "
        "First of all, copy this sheet to your Google Account.\n\n"
        "👉 [Telexpense Template Sheet](https://docs.google.com/spreadsheets/d/1DfLa0vry-8YJVZgdkPDPcQEI6vYm19n2ddTBPNWo7K8/edit#gid=0) 👈",
        parse_mode='Markdown')

    await bot.send_message(
        message.chat.id,
        "Make sure you have added me as an editor, "
        "this is my email:\n\n"
        "telexpense-bot@telexpense-bot.iam.gserviceaccount.com")
     
async def process_url(message: types.Message, state: FSMContext):
    """
    This handler is used to check and add users URL to database.
    """
    # Stop form
    await state.finish()

    await bot.send_message(
        message.chat.id,
        "Checking this sheet...")
    
    # Sheet multilevel check
    if message.text.startswith('https://'):
        user_sheet = Sheet(message.text)
        # Check if bot is able to connect to sheet
        if user_sheet != None:
            # Check if sheet is copied from template
            if user_sheet.is_right_sheet() != False:
                # Insert url to database
                database.insert_sheet_id(
                    message.from_user.id, utils.extract_id_from_url(message.text))
                await bot.send_message(
                    message.chat.id,
                    'Great! You are in!',
                    reply_markup=keyboards.get_main_markup())
                return

    await bot.send_message(
        message.chat.id,
        "Hm. Looks like it's not a link I'm looking for...\n\n"
        "Read the wiki and try to /register one more time!",
        reply_markup=keyboards.get_register_markup())
    