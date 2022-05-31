from asyncio import sleep

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from server import bot

admin_id = int(324769925)


class Mailing(StatesGroup):
    text = State()
    start = State()


# Фича для рассылки по юзерам (учитывая их язык)
#@dp.message_handler(user_id=admin_id, commands=["sendall"])
async def mailing(message: types.Message):
    await message.answer("Пришлите текст сообщения для рассылки")
    await Mailing.text.set()


#@dp.message_handler(user_id=admin_id, state=Mailing.text)
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
        inline_keyboard=
        [
            [InlineKeyboardButton("Начать рассылку", callback_data='start')],
            [InlineKeyboardButton("Отмена", callback_data='cancel')]
        ]
    )

    await bot.send_message(message.from_user.id, f"Сообщение будет выглядеть так:\n\n{text}", parse_mode="Markdown", reply_markup=markup)

    # await message.answer("Пользователям на каком языке разослать это сообщение?\n\n"
    #                        "Текст:\n"
    #                        "{text}").format(text=text),
    #                      reply_markup=markup
    # await Mailing.Language.set()

    await Mailing.start.set()


#@dp.callback_query_handler(user_id=admin_id, state=Mailing.start)
async def mailing_start(call: types.CallbackQuery, state: FSMContext):
    if call.data == "cancel":
        await state.reset_state()
        #await state.finish()

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
        
        users = [324769925]
        
        for user in users:
            try:
                await bot.send_message(user, text, parse_mode='Markdown')
                await sleep(0.3)
            except Exception as e:
                print(e)
                pass
        await call.message.answer("Рассылка выполнена")

def register_admin(dp: Dispatcher):
    dp.register_message_handler(mailing, user_id=admin_id, commands=["sendall"])
    dp.register_message_handler(mailing_text, user_id=admin_id, state=Mailing.text)
    dp.register_callback_query_handler(mailing_start, user_id=admin_id, state=Mailing.start)
