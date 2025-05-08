from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from core.handlers.handlers_utils.share_price_utils import clean_chat
from core.utils.logger import logger
from core.forms.profile_add_share_form import ProfileAddShare

router = Router()


@router.callback_query(F.data == "create_profile")
async def create_profile_handler(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        await state.clear()

        await callback.message.delete()
        await clean_chat(callback.message)

        msg = await callback.message.answer(
            "🚀 Давайте создадим ваш профиль!\nВведите тикер акции:"
        )

        await state.update_data(bot_msg_id=msg.message_id)
        await state.set_state(ProfileAddShare.ADD_SHARE)

    except Exception as outer_exception:
        logger.error(f"Ошибка в create_profile_handler: {outer_exception}")
