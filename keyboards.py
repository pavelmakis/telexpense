from aiogram.types import ReplyKeyboardMarkup

def get_main_markup() -> ReplyKeyboardMarkup:
    main_markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
    main_markup.add("/income", "/expense")
    main_markup.add("/savings", "/total", "/available")
    return main_markup
    
def get_description_markup() -> ReplyKeyboardMarkup:
    description_markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
    description_markup.add("No description")
    return description_markup
