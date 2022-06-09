from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

allowed_patterns = {
    "1,234.00{s}": "#,##0.00[{s}]",
    "1,234.00 {s}": "#,##0.00 [{s}]",
    "1 234.00{s}": "# ##0.00[{s}]",
    "1 234.00 {s}": "# ##0.00 [{s}]",
    "{s}1,234.00": "[{s}]#,##0.00",
    "{s} 1,234.00": "[{s}] #,##0.00",
    "{s}1 234.00": "[{s}]# ##0.00",
    "{s} 1 234.00": "[{s}] # ##0.00",
}


def currencies() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("🇺🇸 USD"), KeyboardButton("🇪🇺 EUR")],
            [KeyboardButton("🇬🇧 GBP"), KeyboardButton("🇷🇺 RUB")],
            [KeyboardButton("🇨🇭 CHF"), KeyboardButton("🇨🇦 CAD")],
            [KeyboardButton("🇨🇿 CZK"), KeyboardButton("🇧🇾 BYN")],
            [KeyboardButton("🇺🇦 UAH"), KeyboardButton("🇰🇿 KZT")],
            [KeyboardButton("Cancel")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    return markup


def curr_formats(sign: str) -> ReplyKeyboardMarkup:
    """Get keyboard with two row buttons from list"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    patterns = list(allowed_patterns.keys())
    for i in range(0, len(allowed_patterns), 2):
        # If there is only one item left...
        if len(allowed_patterns) - i == 1:
            # Adding last item as big button
            markup.add(patterns[-1].format(s=sign))
            break
        # Adding items as two buttons in a row
        markup.add(patterns[i].format(s=sign), patterns[i + 1].format(s=sign))

    return markup
