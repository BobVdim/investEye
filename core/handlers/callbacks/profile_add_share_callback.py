from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from core.forms.profile_form import ProfileForm
from core.services.stock_service import StockService
from core.handlers.share_price_handler import SharePriceHandler
from core.services.profile_service import get_user_profile_from_db

router = Router()


@router.callback_query(F.data == "create_profile")
async def create_profile_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    user_id = callback.from_user.id
    profile_data = get_user_profile_from_db(user_id)

    if not profile_data:
        await state.set_state(ProfileForm.ADD_SHARE)
        await callback.message.answer(
            "🚀 Давайте создадим ваш профиль!\nВведите тикер акции:",
        )

    else:
        service = StockService()
        handler = SharePriceHandler(service)
        await handler.get_price(callback.message, state)
