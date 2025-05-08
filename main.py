import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from core.forms.profile_add_share_form import ProfileAddShare
from core.handlers.profile_add_share_hanlder import add_share_handler, process_add_share, process_add_price, \
    process_add_count
from settings import settings
from core.forms.share_price_form import ShareForm
from core.handlers.start import get_start
from core.handlers.share_price_handler import SharePriceHandler
from core.handlers.handlers_utils.profile_view import get_user_profile_message
from core.services.stock_service import StockService
from core.utils.commands import set_commands
from core.handlers.callbacks.share_price_callback import router as repeat_share_handler
from core.handlers.callbacks.profile_add_share_callback import router as profile_add_share_router
from core.forms.profile_delete_share_form import ProfileDeleteShare
from core.handlers.profile_delete_share_handler import delete_share_handler, process_delete_share, process_delete_count
from core.middleware.reset_state_middleware import ResetStateMiddleware


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - "
               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
    )

    bot = Bot(settings.bots.telegram_bot.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(ResetStateMiddleware())

    await set_commands(bot)

    service = StockService()
    share_handler = SharePriceHandler(service=service)

    dp.include_router(repeat_share_handler)
    dp.include_router(profile_add_share_router)

    dp.message.register(get_start, Command(commands=['start']))
    dp.message.register(share_handler.get_price, Command(commands=['share_price']))
    dp.message.register(get_user_profile_message, Command(commands='profile'))

    dp.message.register(add_share_handler, F.text == "✨ Добавить акцию")
    dp.message.register(process_add_share, ProfileAddShare.ADD_SHARE)
    dp.message.register(process_add_price, ProfileAddShare.ADD_PRICE)
    dp.message.register(process_add_count, ProfileAddShare.ADD_COUNT)

    dp.message.register(delete_share_handler, F.text == "🗑️ Удалить акцию")
    dp.message.register(process_delete_share, ProfileDeleteShare.DELETE_SHARE)
    dp.message.register(process_delete_count, ProfileDeleteShare.DELETE_COUNT)

    dp.message.register(share_handler.get_answer, ShareForm.GET_TICKER)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
