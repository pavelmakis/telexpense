from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def pay_countries_inlkeyb() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🇷🇺 Russia", callback_data="russia"))
    markup.row(InlineKeyboardButton("🌍 Other world", callback_data="other"))
    markup.row(InlineKeyboardButton("Cancel", callback_data="cancel"))

    return markup


def ru_donation_link_inlkeyb() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Pay", url="https://yoomoney.ru/to/4100117828707672")
    )

    return markup
