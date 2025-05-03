from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.utils.logger import logger


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
    Удаляет сообщение пользователя, если оно ещё существует.
    """
    try:
        await message.delete()
    except Exception as e:
        if "message to delete not found" not in str(e):
            logger.warning(f"Не удалось удалить сообщение пользователя: {e}")


async def delete_previous_bot_message(message: Message, state: FSMContext):
    """
    Удаляет последнее сообщение бота, если его ID сохранён в FSMContext.
    """
    try:
        data = await state.get_data()
        old_msg_id = data.get("bot_msg_id")
        if old_msg_id:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=old_msg_id)
            except Exception as e:
                logger.warning(f"Не удалось удалить предыдущее сообщение бота: {e}")
    except Exception as e:
        logger.error(f"Ошибка в delete_previous_bot_message: {e}")
