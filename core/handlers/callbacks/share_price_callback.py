from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from core.handlers.share_price_handler import SharePriceHandler
from core.services.stock_service import StockService

router = Router()


@router.callback_query(F.data == "repeat_share")
async def repeat_share_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    service = StockService()
    handler = SharePriceHandler(service)
    await handler.get_price(callback.message, state)
