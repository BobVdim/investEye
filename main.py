import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command

from settings import TOKEN
from core.forms.share_price_form import ShareForm
from core.handlers.start import get_start
from core.handlers.share_price_handler import SharePriceHandler
from core.services.stock_service import StockService
from core.utils.commands import set_commands


async def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    bot = Bot(TOKEN)
    dp = Dispatcher()
 
    service = StockService()
    share_handler = SharePriceHandler(service=service)

    await set_commands(bot)

    dp.message.register(get_start, Command(commands=['start']))

    dp.message.register(share_handler.get_price, Command(commands=['share_price']))
    dp.message.register(share_handler.get_answer, ShareForm.GET_TICKER)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
