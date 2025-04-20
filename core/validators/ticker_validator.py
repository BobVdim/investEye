from aiogram.types import Message

from core.texts.errors_texts import ERROR


async def validate_ticker(message: Message):
    """Валидация тикера акции"""

    ticker = message.text.strip().upper()
    if not ticker:
        await message.answer(ERROR)
        return None

    return ticker
