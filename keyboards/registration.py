from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def new_sheet_keyb() -> InlineKeyboardMarkup:
    """Get /register menu for unregistered users"""
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Connect new Google Sheet", callback_data="new_sheet")
    )
    markup.row(InlineKeyboardButton("Cancel", callback_data="cancel"))

    return markup


def change_sheet_keyb() -> InlineKeyboardMarkup:
    """Get /register menu for registered users"""
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Change connected Google Sheet", callback_data="new_sheet")
    )
    markup.row(
        InlineKeyboardButton("Forget my Google Sheet", callback_data="forget_sheet")
    )
    markup.row(InlineKeyboardButton("Cancel", callback_data="cancel"))

    return markup


def copytemplate_done_keyb() -> InlineKeyboardMarkup:
    """Get keyboard on registration step 1"""
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Done", callback_data="template_copied"))
    markup.row(InlineKeyboardButton("Cancel", callback_data="cancel"))

    return markup


def addemail_done_keyb() -> InlineKeyboardMarkup:
    """Get keyboard on registration step 2"""
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Done", callback_data="email_added"))
    markup.row(InlineKeyboardButton("Cancel", callback_data="cancel"))

    return markup


def understand_keyb() -> InlineKeyboardMarkup:
    """Get keyboard on forget sheet warning"""
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("I understand", callback_data="user_understands"))
    markup.row(InlineKeyboardButton("Cancel", callback_data="cancel"))

    return markup
