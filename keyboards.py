import sheet

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup

def get_main_markup() -> ReplyKeyboardMarkup:
    main_markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
    main_markup.add("/expense", "/income")
    main_markup.add("/total", "/available")
    return main_markup

def get_accounts_markup() -> ReplyKeyboardMarkup:
    """
    Get keyboard markup with account list from sheets. Places two buttons with
    accounts in a row. If only one account, places it as one button. If no accounts,
    no buttons will be placed. 

    Returns:
        ReplyKeyboardMarkup: keyboard markup with a list of accounts from sheet
    """
    accounts_markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
    # Getting account list from Google sheet
    user_sheet = sheet.Sheet()
    account_list = user_sheet.get_accounts()
    
    # Adding buttons to markup
    for i in range(0, len(account_list), 2):
        if len(account_list) - i == 1:
            # Adding last account as big button
            accounts_markup.add(account_list[-1])
            break
        # Adding accounts as two buttons in a row
        accounts_markup.add(account_list[i], account_list[i+1])
    return accounts_markup

def get_outcome_categories_markup() -> ReplyKeyboardMarkup:
    """
    Get keyboard markup with outcome categories list from sheets. Places two buttons
    with categories in a row. If only one category, places it as one button. If no
    categories, no buttons will be placed. 

    Returns:
        ReplyKeyboardMarkup: keyboard markup with a list of outcome categories from sheet
    """
    out_categories_markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
    # Getting outcome categorues list from Google sheet
    user_sheet = sheet.Sheet()
    out_category_list = user_sheet.get_outcome_categories()
    
    # Adding buttons to markup
    for i in range(0, len(out_category_list), 2):
        if len(out_category_list) - i == 1:
            # Adding last category as big button
            out_categories_markup.add(out_category_list[-1])
            break
        # Adding categories as two buttons in a row
        out_categories_markup.add(out_category_list[i], out_category_list[i+1])
    return out_categories_markup

def get_income_categories_markup() -> ReplyKeyboardMarkup:
    """
    Get keyboard markup with income categories list from sheets. Places two buttons
    with categories in a row. If only one category, places it as one button. If no
    categories, no buttons will be placed. 

    Returns:
        ReplyKeyboardMarkup: keyboard markup with a list of income categories from sheet
    """
    in_categories_markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
    # Getting outcome categorues list from Google sheet
    user_sheet = sheet.Sheet()
    in_category_list = user_sheet.get_income_categories()
    
    # Adding buttons to markup
    for i in range(0, len(in_category_list), 2):
        if len(in_category_list) - i == 1:
            # Adding last category as big button
            in_categories_markup.add(in_category_list[-1])
            break
        # Adding categories as two buttons in a row
        in_categories_markup.add(in_category_list[i], in_category_list[i+1])
    return in_categories_markup
        






