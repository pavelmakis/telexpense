from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message

from config import SHEET_SERVICE_ACCOUNT
from telexpense.sheets import UserSheet
from telexpense.sheets.types import Categories
from telexpense.utils.parsing import parse_amount
from telexpense.utils.sendmessage import send_message


class ExpenseForm(StatesGroup):
    amount = State()
    category = State()
    subcategory = State()
    account = State()


async def answer_expense_btn(msg: Message, state: FSMContext) -> None:
    await send_message(
        chat_id=msg.from_user.id,
        text="Введите сумму расхода или нажмите /отмена",
    )

    await ExpenseForm.amount.set()

    # TODO: Get users service account data and sheet id

    user_sheet = UserSheet(
        SHEET_SERVICE_ACCOUNT, "1B2nzDkv1XH2ziOiiezn0GiakwTwozKj-ojoBg35fpog"
    )

    # Getting today date, categories and accounts from sheet
    # and caching it in state data
    sheet_data = user_sheet.get_data_for_new_record()
    await state.update_data(sheet_data)

    # keyboard = pass


async def process_expense_amount(msg: Message, state: FSMContext) -> None:
    await send_message(
        chat_id=msg.from_user.id,
        text="Какая категория расхода?",
    )

    # Parsing user entered amount
    if (amount := parse_amount(msg.text)) is None:
        ...

    # Saving amount data in state cache
    await state.update_data({"amount": amount})

    # Creating keyboard with categories
    categories: Categories = (await state.get_data())["categories"]
    categories = tuple(categories["expense"].keys())

    print(await state.get_data())
    await state.finish()
    # await ExpenseForm.category.set()


async def process_expense_account(msg: Message, state: FSMContext):
    ...


def register_expense(dp: Dispatcher) -> None:
    dp.register_message_handler(
        answer_expense_btn,
        Text(equals="Expense"),
    )
    dp.register_message_handler(
        process_expense_amount, content_types=["text"], state=ExpenseForm.amount
    )
