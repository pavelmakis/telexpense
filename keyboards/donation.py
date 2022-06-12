from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from server import _


def pay_countries_inlkeyb() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(_("🇷🇺 Russia"), callback_data="russia"))
    markup.row(InlineKeyboardButton(_("🌍 Other world"), callback_data="other"))
    markup.row(InlineKeyboardButton(_("Cancel"), callback_data="cancel"))

    return markup


def ru_donation_link_inlkeyb() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(_("Pay"), url="https://yoomoney.ru/to/4100117828707672")
    )

    return markup
