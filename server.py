import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.message import ContentType

import answers
import keyboards
from handlers.expenses import register_expenses
from handlers.income import register_income
from handlers.registration import register_registration
from handlers.transfer import register_transfer
from handlers.user import register_start_help, register_user

API_TOKEN = os.getenv('TELEXPENSE_TOKEN')
PROVIDER_TOKEN = os.getenv('TELEXPENSE_PROVIDER_TOKEN')
PRICE = [types.LabeledPrice(label="Donate", amount=300)]

# Configure logging
logging.basicConfig(level=logging.INFO)

# def register_all_middlewares(dp):
#     dp.setup_middleware(DbMiddleware())


# def register_all_filters(dp):
#     dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    # Registering commands available for unregistered users
    register_start_help(dp)

    # register_admin(dp)
    
    # Registering commands for registration
    register_registration(dp)

    # Registering comands for all users
    register_user(dp)
    register_expenses(dp)
    register_income(dp)
    register_transfer(dp)
    


# Initialize bot and dispatcher
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


register_all_handlers(dp)


@dp.message_handler(commands=['donate'])
async def send_invoice(message: types.Message):
    # Send help message 
    await bot.send_message(
        message.chat.id,
        answers.donate_mes,
        reply_markup=keyboards.get_main_markup()
    )
    # Send invoice
    await bot.send_invoice(
        message.chat.id,
        title="Donation to developer",
        description=answers.donate_description,
        provider_token=PROVIDER_TOKEN,
        currency='eur',
        is_flexible=False,
        prices=PRICE,
        max_tip_amount=9700,
        suggested_tip_amounts=[200, 700, 1200, 1700],
        payload='Donate invoice sent'
    )

# I have a simple donate button, so I answer OK to query
@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    """Sends thanks message if successfull payment"""
    await bot.send_message(
        message.chat.id,
        answers.successfull_payment.format(
            total_amount=message.successful_payment.total_amount // 100,
            currency=message.successful_payment.currency
        ),
        parse_mode='Markdown',
        reply_markup=keyboards.get_main_markup()
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)