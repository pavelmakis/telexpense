from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.types.input_media import InputMediaVideo
from gspread.utils import extract_id_from_url

import database
import messages
from keyboards import registration
from keyboards.user import main_keyb, register_keyb
from server import _, bot
from sheet import Sheet


class RegistrationForm(StatesGroup):
    """This form if used for registration"""

    option = State()
    connect_new = State()
    get_link = State()
    process_link = State()
    forget = State()


def check_url(message_text: str) -> bool:
    """Sheet template check"""
    if message_text.startswith("https://"):
        user_sheet = Sheet(extract_id_from_url(message_text))
        # Check if bot is able to connect to sheet
        if user_sheet != None:
            # Check if sheet is copied from template
            if user_sheet.is_right_sheet() != False:
                return True
    return False


async def start_registration(message: Message):
    """This handler is used when user sends /register command"""
    # Users get different messages based on if they are
    # registered or not
    if database.is_user_registered(message.from_user.id):
        await message.answer(
            messages.reg_start_registered,
            reply_markup=registration.change_sheet_keyb(),
        )
    else:
        await message.answer(
            messages.reg_start_unregistered,
            reply_markup=registration.new_sheet_keyb(),
        )

    # Setting form on the begining
    await RegistrationForm.option.set()


async def process_user_option(call: CallbackQuery):
    # Answer to query
    await bot.answer_callback_query(call.id)

    if call.data == "new_sheet":
        await bot.send_video(
            # For each bot one file has different file_id. Thats why I need one
            # file_id for my test bot and another for my production bot
            #
            # If you need to get file_id for your bot, send yourself a message with file
            # from you bot using Telegram API in browser. In the result there will be
            # file_id field
            call.from_user.id,
            # for test bot
            #video="CgACAgQAAxkDAAICnmKTrx5fRvoBSbfcmGHrpNOTrmByAAKGAwACxs6cUOdnAc6h666dJAQ",
            # for telexpense
            video="CgACAgQAAxkDAAIk8GKTsJeiKNiFtQV5r3Y5TxnzI6WwAAKGAwACxs6cUJBCE840i8xkJAQ",
            width=1512,
            height=946,
            caption=messages.reg_step_1,
            parse_mode="Markdown",
            reply_markup=registration.copytemplate_done_keyb(),
        )

        # Deleting previous message because I cant edit it
        # because it is media message
        await bot.delete_message(call.from_user.id, call.message.message_id)

        # Setting state
        await RegistrationForm.connect_new.set()

    elif call.data == "forget_sheet":
        # Sending warning to user
        await bot.edit_message_text(
            messages.reg_forget_warning,
            call.from_user.id,
            call.message.message_id,
            reply_markup=registration.understand_keyb(),
        )

        # Setting state
        await RegistrationForm.forget.set()


async def process_cancel(call: CallbackQuery, state: FSMContext):
    # Delete message with inline keyboard
    await bot.delete_message(call.from_user.id, call.message.message_id)

    registered = database.is_user_registered(call.from_user.id)

    # Send message with reply markup
    await bot.send_message(
        call.from_user.id,
        _("OK, next time"),
        reply_markup=main_keyb() if registered else register_keyb(),
    )

    # End state machine
    await state.finish()


async def add_bot_email(call: CallbackQuery):
    # Answer to query
    await bot.answer_callback_query(call.id)

    await bot.edit_message_media(
        InputMediaVideo(
            # for test bot
            #"CgACAgQAAxkDAAICpmKTsnx3QJm2mI8cA61YzzZpK9IyAAJtAwAC7SukUMWd2HYBF9nqJAQ",
            # for telexpense
            "CgACAgQAAxkDAAIk-2KTuhq5jmAyOt2GS2xD73Vo6cCIAAJtAwAC7SukULuOaMN-Ao5_JAQ",
            caption=messages.reg_step_2,
            parse_mode="Markdown",
        ),
        call.from_user.id,
        call.message.message_id,
        reply_markup=registration.addemail_done_keyb(),
    )

    await RegistrationForm.get_link.set()


async def ask_sheet_url(call: CallbackQuery):
    # Answer to query
    await bot.answer_callback_query(call.id)

    # Send message with step 3 of instructions
    await bot.send_message(
        call.from_user.id,
        messages.reg_step_3,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Delete previous message
    await bot.delete_message(
        call.from_user.id,
        call.message.message_id,
    )

    await RegistrationForm.process_link.set()


async def process_sheet_url(message: Message, state: FSMContext):
    # Stop form
    await state.finish()

    await message.answer(_("Checking this sheet..."))

    registered = database.is_user_registered(message.from_user.id)

    # Sheet check
    if check_url(message.text):
        if registered:
            # Removing previous record if user was registered
            #TODO: Update db record, not rewrite
            database.delete_sheet_id(message.from_user.id)

            database.insert_sheet_id(
                message.from_user.id, extract_id_from_url(message.text)
            )

            await message.answer(
                messages.reg_update_success,
                reply_markup=main_keyb(),
            )
        else:
            database.insert_sheet_id(
                message.from_user.id, extract_id_from_url(message.text)
            )
            await message.answer(messages.reg_success, reply_markup=main_keyb())

        return

    await message.answer(
        messages.reg_wrong_link,
        disable_web_page_preview=True,
        parse_mode="Markdown",
        reply_markup=main_keyb() if registered else register_keyb(),
    )


async def forget_user_sheet(call: CallbackQuery, state: FSMContext):
    # Answer to query
    await bot.delete_message(call.from_user.id, call.message.message_id)

    # End state machine
    await state.finish()

    # Delete user from database
    database.delete_sheet_id(call.from_user.id)

    await bot.send_message(
        call.from_user.id,
        _("See you next time!"),
        reply_markup=register_keyb(),
    )


def register_registration(dp: Dispatcher):
    dp.register_message_handler(start_registration, commands=["register"])
    dp.register_callback_query_handler(
        process_cancel,
        lambda c: c.data and c.data == "cancel",
        state=RegistrationForm.all_states,
    )
    dp.register_callback_query_handler(
        process_user_option, state=RegistrationForm.option
    )
    dp.register_callback_query_handler(
        forget_user_sheet,
        lambda c: c.data and c.data == "user_understands",
        state=RegistrationForm.forget,
    )
    dp.register_callback_query_handler(
        add_bot_email,
        lambda c: c.data and c.data == "template_copied",
        state=RegistrationForm.connect_new,
    )
    dp.register_callback_query_handler(
        ask_sheet_url,
        lambda c: c.data and c.data == "email_added",
        state=RegistrationForm.get_link,
    )
    dp.register_message_handler(process_sheet_url, state=RegistrationForm.process_link)
