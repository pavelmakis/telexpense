import os
from asyncio import sleep

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import database
from server import bot

admin_id = int(os.getenv("ADMIN_ID"))


class Mailing(StatesGroup):
    text = State()
    start = State()


async def mailing(message: types.Message):
    await message.answer("Пришлите текст сообщения для рассылки")
    await Mailing.text.set()


async def mailing_text(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)
    # markup = InlineKeyboardMarkup(
    #     inline_keyboard=
    #     [
    #         [InlineKeyboardButton(text="Русский", callback_data="ru")],
    #         [InlineKeyboardButton(text="English", callback_data="en")],
    #         [InlineKeyboardButton(text="Україньска", callback_data="uk")],
    #     ]
    # )

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Начать рассылку", callback_data="start")],
            [InlineKeyboardButton("Отмена", callback_data="cancel")],
        ]
    )

    await bot.send_message(
        message.from_user.id,
        f"Сообщение будет выглядеть так:\n\n{text}",
        parse_mode="Markdown",
        reply_markup=markup,
    )

    # await message.answer("Пользователям на каком языке разослать это сообщение?\n\n"
    #                        "Текст:\n"
    #                        "{text}").format(text=text),
    #                      reply_markup=markup
    # await Mailing.Language.set()

    await Mailing.start.set()


async def mailing_start(call: types.CallbackQuery, state: FSMContext):
    if call.data == "cancel":
        await state.reset_state()
        # await state.finish()

        await bot.edit_message_text(
            "OK, cancelled!",
            call.from_user.id,
            call.message.message_id,
        )
    else:
        data = await state.get_data()
        text = data.get("text")
        await state.reset_state()
        await call.message.edit_reply_markup()

        users = database.get_all_users()
        sent_counter, del_counter = 0, 0

        for user in users:
            try:
                await bot.send_message(
                    user, text, disable_notification=True, parse_mode="Markdown"
                )

                await sleep(0.3)
            except Exception:
                # database.delete_sheet_id()
                del_counter += 1
                continue
            sent_counter += 1
        await call.message.answer(
            "Рассылка завершена.\n\n"
            f"Сообщение отправлено {sent_counter} раз, "
            f"{del_counter} пользователей удалено."
        )

async def count_users(message: Message):
    users = len(database.get_all_users())

    await message.answer(f"Пользователей в базе: {users}")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(mailing, user_id=admin_id, commands=["sendall"])
    dp.register_message_handler(mailing_text, user_id=admin_id, state=Mailing.text)
    dp.register_callback_query_handler(
        mailing_start, user_id=admin_id, state=Mailing.start
    )
    dp.register_message_handler(count_users, user_id=admin_id, commands=["countusers"])
