from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from core.handlers.handlers_utils.profile_view import get_user_profile_message
from core.forms.profile_view_mode_form import ProfileViewMode


async def change_view_to_pc(message: Message, state: FSMContext):
    await state.update_data(view_mode="pc")
    await state.set_state(ProfileViewMode.PC_VIEW)
    await get_user_profile_message(message, state)


async def change_view_to_mobile(message: Message, state: FSMContext):
    await state.update_data(view_mode="mobile")
    await state.set_state(ProfileViewMode.MOBILE_VIEW)
    await get_user_profile_message(message, state)
