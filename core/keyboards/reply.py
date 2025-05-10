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
    ],
    [
        KeyboardButton(
            text='🖥️ Вид для ПК'
        ),
        KeyboardButton(
            text='📱 Вид для телефона'
        )
    ],
], resize_keyboard=True, input_field_placeholder='Редактировать профиль')
