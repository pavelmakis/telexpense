from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


def get_main_markup() -> ReplyKeyboardMarkup:
    """Get main keyboard"""
    main_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    main_markup.add("➕Income", "➖Expense")
    main_markup.add("💱Transfer")
    main_markup.add("💲Available")
    return main_markup


def get_description_markup() -> ReplyKeyboardMarkup:
    """Get keyboard with 'No description' button"""
    description_markup = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    )
    description_markup.add("No description")
    return description_markup


def get_same_amount_markup() -> ReplyKeyboardMarkup:
    """Get keyboard with 'Same amount' button"""
    description_markup = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    )
    description_markup.add("Same amount")
    return description_markup


def get_register_markup() -> ReplyKeyboardMarkup:
    """Get keyboard with '/register' button"""
    register_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    register_markup.add("/register")
    return register_markup

def get_new_sheet_inlmarkup() -> InlineKeyboardMarkup:
    new_sheet_inlmarkup = InlineKeyboardMarkup()

    btn_1 = InlineKeyboardButton("Connect new Google Sheet", callback_data="new_sheet")
    btn_2 = InlineKeyboardButton("Cancel", callback_data="cancel")
    new_sheet_inlmarkup.row(btn_1)
    new_sheet_inlmarkup.row(btn_2)
    return new_sheet_inlmarkup

def get_change_sheet_inlmarkup() -> InlineKeyboardMarkup:
    change_sheet_inlmarkup = InlineKeyboardMarkup()
    
    btn_1 = InlineKeyboardButton("Change connected Google Sheet", callback_data="new_sheet")
    btn_2 = InlineKeyboardButton("Forget my Google Sheet", callback_data="forget_sheet")
    btn_3 = InlineKeyboardButton("Cancel", callback_data="cancel")
    change_sheet_inlmarkup.row(btn_1)
    change_sheet_inlmarkup.row(btn_2)
    change_sheet_inlmarkup.row(btn_3)
    return change_sheet_inlmarkup

def get_copytemplate_done_inlmarkup() -> InlineKeyboardMarkup:
    template_done_inlmarkup = InlineKeyboardMarkup()
    btn_done = InlineKeyboardButton("Done", callback_data='template_copied')
    btn_cncl = InlineKeyboardButton("Cancel", callback_data='cancel')
    template_done_inlmarkup.row(btn_done)
    template_done_inlmarkup.row(btn_cncl)
    return template_done_inlmarkup

def get_addemail_done_inlmarkup() -> InlineKeyboardMarkup:
    email_done_inlmarkup = InlineKeyboardMarkup()
    btn_done = InlineKeyboardButton("Done", callback_data='email_added')
    btn_cncl = InlineKeyboardButton("Cancel", callback_data='cancel')
    email_done_inlmarkup.row(btn_done)
    email_done_inlmarkup.row(btn_cncl)

    return email_done_inlmarkup

def get_understand_inlmarkup() -> InlineKeyboardMarkup:
    understand_inlmarkup = InlineKeyboardMarkup()
    btn_undr = InlineKeyboardButton("I understand", callback_data='user_understands')
    btn_cncl = InlineKeyboardButton("Cancel", callback_data='cancel')
    understand_inlmarkup.row(btn_undr)
    understand_inlmarkup.row(btn_cncl)

    return understand_inlmarkup

def get_pay_countries_inlmarkup() -> InlineKeyboardMarkup:
    pay_countries_inlmarkup = InlineKeyboardMarkup()
    btn_ru = InlineKeyboardButton("🇷🇺 Russia", callback_data='russia')
    btn_other = InlineKeyboardButton("🌍 Other world", callback_data='other')
    btn_cncl = InlineKeyboardButton("Cancel", callback_data='cancel')
    pay_countries_inlmarkup.row(btn_ru)
    pay_countries_inlmarkup.row(btn_other)
    pay_countries_inlmarkup.row(btn_cncl)

    return pay_countries_inlmarkup

def get_rus_donation_link_inlmarkup() -> InlineKeyboardMarkup:
    rus_donation_link_inlmarkup = InlineKeyboardMarkup()
    btn_payment_link = InlineKeyboardButton("Pay", url="https://yoomoney.ru/to/4100117828707672")
    rus_donation_link_inlmarkup.row(btn_payment_link)

    return rus_donation_link_inlmarkup

def get_cancel_markup() -> ReplyKeyboardMarkup:
    """Get keyboard with 'Cancel' button"""
    cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    cancel_markup.add("Cancel")
    return cancel_markup


def get_two_row_keyboard(buttons: list) -> ReplyKeyboardMarkup:
    """Get keyboard with two row buttons from list"""
    buttons_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in range(0, len(buttons), 2):
        # If there is only one item left...
        if len(buttons) - i == 1:
            # Adding last item as big button
            buttons_markup.add(buttons[-1])
            break
        # Adding items as two buttons in a row
        buttons_markup.add(buttons[i], buttons[i + 1])

    return buttons_markup
