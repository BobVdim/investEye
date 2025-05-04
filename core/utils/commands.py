from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Начало работы'
        ),
        BotCommand(
            command='share_price',
            description='Информация о стоимости акции'
        ),
        BotCommand(
            command='profile',
            description='Мой профиль'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
