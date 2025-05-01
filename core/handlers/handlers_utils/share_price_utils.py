from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.utils.logger import logger
from core.forms.share_price_form import ShareForm

""" Утилиты для работы share_price_handler """


async def send_response(message: Message, text: str, parse_mode: str = 'HTML', reply_markup=None):
    """ Отправляет текстовое сообщение пользователю в Telegram """

    try:
        await message.answer(text, parse_mode=parse_mode, reply_markup=reply_markup)
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


async def edit_old_bot_message(message: Message, state: FSMContext, new_text: str, parse_mode: str = 'HTML',
                               reply_markup=None):
    """ Редактирует старое сообщение бота """

    data = await state.get_data()
    msg_id = data.get("msg_id")
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text=new_text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.warning(f"Не удалось отредактировать сообщение бота: {e}")
            await message.answer(new_text, parse_mode=parse_mode, reply_markup=reply_markup)
    else:
        await message.answer(new_text, parse_mode=parse_mode, reply_markup=reply_markup)
