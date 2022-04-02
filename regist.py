"""
This file contains aiogram handlers for user registration.
When user registers into bot, his Google sheet URL is added to database.
"""
import os
import logging
import database
import keyboards
import answers
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
    change = State()
    url = State()

def check_url(message_text: str) -> bool:
    """Sheet template check"""
    if message_text.startswith('https://'):
            user_sheet = Sheet(utils.extract_id_from_url(message_text))
            # Check if bot is able to connect to sheet
            if user_sheet != None:
                # Check if sheet is copied from template
                if user_sheet.is_right_sheet() != False:
                    return True
    return False

async def start_registering(message: types.Message):
    """
    This handler is used to ask user his sheet URL
    """

    # If user is already registered
    if database.is_user_registered(message.from_user.id):
        await bot.send_message(
            message.chat.id,
            "I know you! You are already registered!)\n\n"
            'If you would like to connect me to another sheet, send me new link '
            'or tap "Cancel" to cancel.',
            reply_markup=keyboards.get_cancel_markup())
        
        await bot.send_message(
            message.chat.id,
            answers.register_start,
            parse_mode='Markdown')

        await bot.send_message(
            message.chat.id,
            answers.register_email)
        

        # Send user to url change handler
        await URLForm.change.set()
        return

    # Starting form filling
    await URLForm.url.set()
    await bot.send_message(
        message.chat.id,
        answers.register_start,
        parse_mode='Markdown')

    await bot.send_message(
        message.chat.id,
        answers.register_email)
     
async def process_url(message: types.Message, state: FSMContext):
    """
    This handler is used to check and add users URL to database.
    """
    # Stop form
    await state.finish()

    await bot.send_message(
        message.chat.id,
        "Checking this sheet...")
    
    # Sheet check
    if check_url(message.text):
        # Inserting sheet id
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
    
async def change_sheet(message: types.Message, state: FSMContext):
    """
    This handler is used for changing sheet id in database
    """
    # Stop form
    await state.finish()

    # If user cancels
    if message.text.lower() == "cancel":
        await bot.send_message(
            message.chat.id,
            "Ok, cancelled!",
            reply_markup=keyboards.get_main_markup())
        return

    # Sheet check
    if check_url(message.text):
        # Deleting previous record
        database.delete_sheet_id(message.from_user.id)

        # Adding new sheet id
        database.insert_sheet_id(
            message.from_user.id, utils.extract_id_from_url(message.text))

        await bot.send_message(
            message.chat.id,
            'Great! Your sheet successfully changed!',
            reply_markup=keyboards.get_main_markup())
        return
    
    await bot.send_message(
        message.chat.id,
        "Hm. Looks like it's not a link I'm looking for...\n\n"
        "Read the wiki and try to /register one more time!",
        reply_markup=keyboards.get_main_markup())