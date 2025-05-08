from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

add_share_button = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='✨ Добавить акцию'
        )
    ],
    [
        KeyboardButton(
            text='🗑️ Удалить акцию'
        )
    ]
], resize_keyboard=True, input_field_placeholder='Редактировать профиль')
