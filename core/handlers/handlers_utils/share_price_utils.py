from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.utils.logger import logger
from core.forms.share_price_form import ShareForm


async def send_one_message(
        message: Message,
        state: FSMContext,
        text: str,
        reply_markup=None,
        parse_mode: str = 'HTML'
):
    """
    Удаляет предыдущее сообщение бота (если оно есть) и отправляет новое.
    Сохраняет ID нового сообщения в FSM-состоянии.
    """

    try:
        data = await state.get_data()
        old_msg_id = data.get("bot_msg_id")

        if old_msg_id:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=old_msg_id)
            except Exception as e:
                logger.warning(f"Не удалось удалить предыдущее сообщение бота: {e}")

        new_msg = await message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)

        await state.update_data(bot_msg_id=new_msg.message_id)

    except Exception as e:
        logger.error(f"Ошибка в send_one_message: {e}")


async def clean_chat(message: Message):
    """
    Удаляет сообщение пользователя.
    """

    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение пользователя: {e}")


async def set_state(state: FSMContext, msg_id: int):
    """
    Сохраняет ID текущего сообщения бота и устанавливает состояние FSM.
    """

    await state.update_data(msg_id=msg_id)
    await state.set_state(ShareForm.GET_TICKER)
