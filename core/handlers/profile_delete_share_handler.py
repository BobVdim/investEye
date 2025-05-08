import sqlite3

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.forms.profile_delete_share_form import ProfileDeleteShare
from core.services.profile_service import delete_share_from_db, delete_share_count_in_db, get_user_profile_from_db
from core.handlers.handlers_utils.share_price_utils import send_one_message, delete_previous_bot_message, clean_chat
from core.keyboards.reply import add_share_button
from core.handlers.handlers_utils.profile_view import build_profile_text


async def delete_share_handler(message: Message, state: FSMContext):
    await clean_chat(message)
    await delete_previous_bot_message(message, state)

    await send_one_message(message, state, text="Введите тикер акции, которую хотите удалить:")
    await state.set_state(ProfileDeleteShare.DELETE_SHARE)


async def process_delete_share(message: Message, state: FSMContext):
    await clean_chat(message)
    await delete_previous_bot_message(message, state)

    ticker = message.text.strip().upper()
    await state.update_data(share=ticker)

    user_id = message.from_user.id
    conn = sqlite3.connect("my_bd")
    cursor = conn.cursor()
    cursor.execute("SELECT count FROM profile WHERE id = ? AND share = ?", (user_id, ticker))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        await send_one_message(message, state, text="❌ У вас нет акций с таким тикером.")
        return

    current_count = result[0]

    await send_one_message(message, state,
                           text=f"Текущее количество акций {ticker}: {current_count}(шт).\n\n"
                                f"Введите количество для удаления (или 'all' для полной продажи):")
    await state.set_state(ProfileDeleteShare.DELETE_COUNT)


async def process_delete_count(message: Message, state: FSMContext):
    await clean_chat(message)
    await delete_previous_bot_message(message, state)

    user_id = message.from_user.id
    user_data = await state.get_data()
    ticker = user_data.get("share")

    count_text = message.text.strip().lower()

    if count_text == "all":
        delete_share_from_db(user_id, ticker)
    else:
        try:
            count = int(count_text)
            if count <= 0:
                raise ValueError
            success = delete_share_count_in_db(user_id, ticker, count)
            if not success:
                await send_one_message(message, state, text="❌ Ошибка при удалении.")
                return
        except ValueError:
            await send_one_message(message, state, text="❌ Введите корректное количество или 'all'.")
            return

    profile_data = get_user_profile_from_db(user_id)
    text = build_profile_text(profile_data)

    await send_one_message(
        message,
        state,
        text=f"{text}",
        reply_markup=add_share_button
    )
