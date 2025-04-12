from aiogram.types import Message


async def get_start(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}! Добро пожаловать в бота.')
