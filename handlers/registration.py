from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
from gspread import utils

import database
import keyboards
import messages
from sheet import Sheet


class URLForm(StatesGroup):
    """
    This form is used for URL getter form.
    """

    change = State()
    url = State()


def check_url(message_text: str) -> bool:
    """Sheet template check"""
    if message_text.startswith("https://"):
        user_sheet = Sheet(utils.extract_id_from_url(message_text))
        # Check if bot is able to connect to sheet
        if user_sheet != None:
            # Check if sheet is copied from template
            if user_sheet.is_right_sheet() != False:
                return True
    return False


async def start_registering(message: Message):
    """
    This handler is used to ask user his sheet URL
    """

    # If user is already registered
    if database.is_user_registered(message.from_user.id):
        await message.answer(
            "I know you! You are already registered!)\n\n"
            "If you would like to connect me to another sheet, send me new link "
            'or tap "Cancel" to cancel.',
            reply_markup=keyboards.get_cancel_markup(),
        )

        await message.answer(
            messages.register_start, disable_web_page_preview=True, parse_mode="Markdown"
        )

        await message.answer(messages.register_email)

        # Send user to url change handler
        await URLForm.change.set()
        return

    # Starting form filling
    await URLForm.url.set()
    await message.answer(messages.register_start, parse_mode="Markdown")

    await message.answer(messages.register_email)


async def process_url(message: Message, state: FSMContext):
    """
    This handler is used to check and add users URL to database.
    """
    # Stop form
    await state.finish()

    await message.answer("Checking this sheet...")

    # Sheet check
    if check_url(message.text):
        # Inserting sheet id
        database.insert_sheet_id(
            message.from_user.id, utils.extract_id_from_url(message.text)
        )

        await message.answer(
            "Great! You are in!", reply_markup=keyboards.get_main_markup()
        )
        return

    await message.answer(
        messages.reg_wrong_link,
        reply_markup=keyboards.get_register_markup(),
    )


async def change_sheet(message: Message, state: FSMContext):
    """
    This handler is used for changing sheet id in database
    """
    # Stop form
    await state.finish()

    # If user cancels
    if message.text.lower() == "cancel":
        await message.answer("Ok, cancelled!", reply_markup=keyboards.get_main_markup())
        return

    # Sheet check
    if check_url(message.text):
        # Deleting previous record
        database.delete_sheet_id(message.from_user.id)

        # Adding new sheet id
        database.insert_sheet_id(
            message.from_user.id, utils.extract_id_from_url(message.text)
        )

        await message.answer(
            messages.reg_sheet_changed,
            reply_markup=keyboards.get_main_markup(),
        )
        return

    await message.answer(
        messages.reg_wrong_link,
        reply_markup=keyboards.get_main_markup(),
    )


def register_registration(dp: Dispatcher):
    dp.register_message_handler(start_registering, commands=["register"])
    dp.register_message_handler(process_url, state=URLForm.url)
    dp.register_message_handler(change_sheet, state=URLForm.change)
