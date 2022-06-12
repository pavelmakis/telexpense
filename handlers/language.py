from aiogram import Dispatcher
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import database
from keyboards.user import main_keyb
from server import _, bot


async def cmd_language(message: Message):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(_("Cancel"), callback_data="cancel")],
        ]
    )

    await message.answer(_("Choose bot's language"), reply_markup=markup)


async def process_language(call: CallbackQuery):
    await bot.answer_callback_query(call.id)

    # If users cancels
    if call.data == "cancel":
        # Answer to user
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(
            call.from_user.id, _("OK, mext time"), reply_markup=main_keyb()
        )

        return

    # Updating user language in database
    await bot.edit_message_text(
        _("Setting selected language..."), call.from_user.id, call.message.message_id
    )

    # Writing language to database
    database.update_language(str(call.from_user.id), call.data[-2:])

    await bot.send_message(call.from_user.id, _("Success!"), reply_markup=main_keyb())
    await bot.delete_message(call.from_user.id, call.message.message_id)


def register_language_cmd(dp: Dispatcher):
    dp.register_message_handler(cmd_language, commands=["language"])
    dp.register_callback_query_handler(
        process_language,
        lambda c: c.data and c.data in ["lang_ru", "lang_en", "cancel"],
    )
