from aiogram.types import ReplyKeyboardMarkup

def get_main_markup() -> ReplyKeyboardMarkup:
    main_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    main_markup.add("➕Income", "➖Expense")
    main_markup.add("💱Transaction")  
    main_markup.add("/savings", "/total", "💲Available")
    return main_markup
    
def get_description_markup() -> ReplyKeyboardMarkup:
    description_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    description_markup.add("No description")
    return description_markup

def get_same_amount_markup() -> ReplyKeyboardMarkup:
    description_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    description_markup.add("Same amount")
    return description_markup

def get_register_markup() -> ReplyKeyboardMarkup:
    register_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    register_markup.add("/register")
    return register_markup

def get_two_row_keyboard(buttons: list) -> ReplyKeyboardMarkup:
    buttons_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in range(0, len(buttons), 2):
        # If there is only one item left...
        if len(buttons) - i == 1:
            # Adding last item as big button
            buttons_markup.add(buttons[-1])
            break
        # Adding items as two buttons in a row
        buttons_markup.add(buttons[i], buttons[i+1])
    
    return buttons_markup
