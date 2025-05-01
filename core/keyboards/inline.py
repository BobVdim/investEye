from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_repeat_share_inline():
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text='🔄 Новый запрос',
            callback_data='repeat_share'
        )
    )

    builder.adjust(1)
    return builder.as_markup()
