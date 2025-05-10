import sqlite3

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.forms.profile_delete_share_form import ProfileDeleteShare
from core.forms.profile_view_mode_form import ProfileViewMode
from core.services.profile_service import delete_share_from_db, delete_share_count_in_db, get_user_profile_from_db
from core.handlers.handlers_utils.share_price_utils import send_one_message, delete_previous_bot_message, clean_chat
from core.keyboards.reply import add_share_button
from core.handlers.handlers_utils.profile_view import (
    build_profile_text_pc,
    build_profile_text_mobile,
    send_profile_empty_message
)
from core.texts import profile_texts


async def delete_share_handler(message: Message, state: FSMContext):
    await clean_chat(message)
    await delete_previous_bot_message(message, state)

    await send_one_message(message, state, text=profile_texts.ENTER_TICKER_TO_DELETE)
    await state.set_state(ProfileDeleteShare.DELETE_SHARE)


async def process_delete_share(message: Message, state: FSMContext):
    await clean_chat(message)
    await delete_previous_bot_message(message, state)

    ticker = message.text.strip().upper()

    if ticker == "ALL":
        user_id = message.from_user.id
        conn = sqlite3.connect("my_bd")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM profile WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

        data = await state.get_data()
        view_mode = data.get("view_mode", "pc")

        await state.clear()
        await state.update_data(view_mode=view_mode)

        if view_mode == "mobile":
            await state.set_state(ProfileViewMode.MOBILE_VIEW)
        else:
            await state.set_state(ProfileViewMode.PC_VIEW)

        await send_profile_empty_message(message, state)
        return

    await state.update_data(share=ticker)

    user_id = message.from_user.id
    conn = sqlite3.connect("my_bd")
    cursor = conn.cursor()
    cursor.execute("SELECT count FROM profile WHERE id = ? AND share = ?", (user_id, ticker))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        await send_one_message(message, state, text=profile_texts.SHARE_NOT_FOUND)
        await state.set_state(ProfileDeleteShare.DELETE_SHARE)
        return

    current_count = result[0]

    await send_one_message(
        message,
        state,
        text=profile_texts.CURRENT_SHARE_COUNT.format(ticker=ticker, count=current_count)
    )
    await state.set_state(ProfileDeleteShare.DELETE_COUNT)


async def process_delete_count(message: Message, state: FSMContext):
    await clean_chat(message)
    await delete_previous_bot_message(message, state)

    user_id = message.from_user.id
    user_data = await state.get_data()
    ticker = user_data.get("share")
    view_mode = user_data.get("view_mode", "pc")

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
                await send_one_message(message, state, text=profile_texts.DELETE_ERROR)
                return
        except ValueError:
            await send_one_message(message, state, text=profile_texts.INVALID_DELETE_COUNT)
            await state.set_state(ProfileDeleteShare.DELETE_COUNT)
            return

    profile_data = get_user_profile_from_db(user_id)

    if not profile_data:
        await send_profile_empty_message(message, state)
        return

    if view_mode == "mobile":
        text = build_profile_text_mobile(profile_data)
    else:
        text = build_profile_text_pc(profile_data)

    await send_one_message(message, state, text=text, reply_markup=add_share_button)
