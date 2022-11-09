from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from telexpense.keyboards import Keyboard


class MainpageKeyboard(Keyboard):
    """Main page keyboard

    0: "Expense",
    1: "Income",
    2: "Transfer",
    3: "Balance",
    """

    def __init__(self) -> None:
        self.buttons = {
            0: "Income",
            1: "Expense",
            2: "Transfer",
            3: "Balance",
        }

    def as_markup(self) -> ReplyKeyboardMarkup:
        markup = ReplyKeyboardMarkup(
            [
                [KeyboardButton(self.buttons[0]), KeyboardButton(self.buttons[1])],
                [KeyboardButton(self.buttons[2])],
                [KeyboardButton(self.buttons[3])],
            ],
            resize_keyboard=True,
        )

        return markup
