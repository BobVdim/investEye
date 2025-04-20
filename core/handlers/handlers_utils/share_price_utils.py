from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.utils.logger import logger
from core.forms.share_price_form import ShareForm

""" Утилиты для работы share_price_handler """


async def send_response(message: Message, text: str, parse_mode: str = 'HTML'):
    """ Отправляет текстовое сообщение пользователю в Telegram """

    try:
        await message.answer(text, parse_mode=parse_mode)
    except Exception as e:
        logger.error(f"Произошла ошибка при отправке сообщения: {e}")


async def clean_chat(message: Message):
    """ Удаляет сообщение пользователя """

    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение пользователя: {e}")


async def set_state(state: FSMContext, msg_id: int):
    """ Устанавливает состояние FSM для пользователя и сохраняет msg_id в контексте """

    await state.update_data(msg_id=msg_id)
    await state.set_state(ShareForm.GET_TICKER)


async def delete_old_bot_message(message: Message, state: FSMContext):
    """ Удаляет предыдущее сообщение бота (избавляет от захламления в чате) """

    data = await state.get_data()
    msg_id = data.get("msg_id")
    if msg_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        except Exception:
            logger.warning("Не удалось предыдущее сообщение бота")
