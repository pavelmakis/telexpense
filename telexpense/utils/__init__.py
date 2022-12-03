import sentry_sdk
from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.exceptions import Unauthorized

from bot import bot


async def send_message(
    chat_id: int,
    text: str,
    parse_mode: str = None,
    disable_web_page_preview: bool = None,
    disable_notification: bool = None,
    protect_content: bool = None,
    reply_to_message_id: int = None,
    allow_sending_without_reply: bool = None,
    reply_markup: ReplyKeyboardMarkup
    | InlineKeyboardMarkup
    | ReplyKeyboardRemove
    | ForceReply = None,
) -> None:
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            protect_content=protect_content,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
        )
    except Unauthorized:
        pass
    except Exception as e:
        sentry_sdk.capture_exception(e)
