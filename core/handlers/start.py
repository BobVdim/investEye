from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from core.texts.start_texts import START_MESSAGE
from core.handlers.handlers_utils.share_price_utils import send_one_message, delete_previous_bot_message


async def get_start(message: Message, state: FSMContext):
    await delete_previous_bot_message(message, state)
    await state.clear()

    await send_one_message(
        message,
        state,
        text=START_MESSAGE.format(name=message.from_user.first_name)
    )
