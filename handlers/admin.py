import os
from asyncio import sleep

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import database
from keyboards.user import main_keyb
from server import bot

admin_id = int(os.getenv("ADMIN_ID"))


class Mailing(StatesGroup):
    language = State()
    text = State()
    start = State()


async def mailing(message: Message):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Английский", callback_data="send_en")],
            [InlineKeyboardButton("Русский", callback_data="send_ru")],
            [InlineKeyboardButton("Отмена", callback_data="cancel")],
        ]
    )

    await message.answer("На каком языке будет рассылка?", reply_markup=markup)

    await Mailing.language.set()


async def mailing_lang(call: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)

    if call.data == "cancel":
        await state.reset_state()
        await state.finish()

        await bot.send_message(
            call.from_user.id,
            "Отменено",
            reply_markup=main_keyb(),
        )

        await bot.delete_message(call.from_user.id, call.message.message_id)

        return

    await state.update_data(lang=call.data[-2:])

    await call.message.answer("Пришлите текст сообщения для рассылки")

    await Mailing.text.set()


async def mailing_text(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)

    async with state.proxy() as data:
        lang = data["lang"]

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Начать рассылку", callback_data="start")],
            [InlineKeyboardButton("Отмена", callback_data="cancel")],
        ]
    )

    await bot.send_message(
        message.from_user.id,
        f"Сообщение для пользователей с языком {lang}:\n\n{text}",
        parse_mode="Markdown",
        reply_markup=markup,
    )

    await Mailing.start.set()


async def mailing_start(call: types.CallbackQuery, state: FSMContext):
    if call.data == "cancel":
        await state.reset_state()
        # await state.finish()

        await bot.edit_message_text(
            "Отменено",
            call.from_user.id,
            call.message.message_id,
        )
    else:
        data = await state.get_data()
        text = data.get("text")
        lang = data.get("lang")

        await state.reset_state()
        await call.message.edit_reply_markup()

        users = database.get_users_by_language(str(lang))
        sent_counter, del_counter = 0, 0

        for user in users:
            try:
                await bot.send_message(
                    user, text, disable_notification=True, parse_mode="Markdown"
                )

                await sleep(0.3)
            except Exception as e:
                print(e)
                # database.delete_sheet_id(user)
                del_counter += 1
                continue
            sent_counter += 1

        await call.message.answer(
            "Рассылка завершена.\n\n"
            f"Сообщение отправлено {sent_counter} раз, "
            f"{del_counter} пользователей удалено.",
            reply_markup=main_keyb(),
        )


async def count_users(message: Message):
    users = database.get_user_count()
    await message.answer(f"Пользователей в базе: {users}")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(mailing, user_id=admin_id, commands=["sendall"])
    dp.register_callback_query_handler(
        mailing_lang, user_id=admin_id, state=Mailing.language
    )
    dp.register_message_handler(mailing_text, user_id=admin_id, state=Mailing.text)
    dp.register_callback_query_handler(
        mailing_start, user_id=admin_id, state=Mailing.start
    )

    dp.register_message_handler(count_users, user_id=admin_id, commands=["countusers"])
