from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from core.keyboards.reply import add_share_button
from core.services.profile_service import get_user_profile_from_db
from core.handlers.handlers_utils.share_price_utils import (
    clean_chat,
    send_one_message,
    delete_previous_bot_message,
)
from core.keyboards.inline import create_profile_inline
from core.utils.logger import logger
from core.texts.profile_texts import (
    PROFILE_EMPTY,
    PROFILE_SUMMARY,
    TABLE_HEADER,
    TABLE_SEPARATOR,
)
from core.texts.errors_texts import ERROR_GET_PROFILE


async def get_user_profile_message(message: Message, state: FSMContext):
    try:
        await delete_previous_bot_message(message, state)
        await clean_chat(message)

        user_id = message.from_user.id
        profile_data = get_user_profile_from_db(user_id)

        if not profile_data:
            await send_profile_empty_message(message, state)
            return

        text = build_profile_text(profile_data)
        await send_one_message(
            message,
            state,
            text=text,
            reply_markup=add_share_button
        )

    except Exception:
        logger.exception("Ошибка в get_user_profile_message")
        await send_one_message(message, state, text=ERROR_GET_PROFILE)


def build_profile_text(rows: list[tuple]) -> str:
    total_value = 0
    table_lines = [TABLE_HEADER, TABLE_SEPARATOR]

    for share, price, count in rows:
        if price is None or count is None:
            continue

        total = round(price * count, 2)
        total_value += total

        formatted_price = f"{price:.2f}"

        line = f"{share.upper():<6} | {formatted_price:<9} | {count:<6} | {total:<10.2f}"
        table_lines.append(line)

    table_str = "\n".join(table_lines)
    return PROFILE_SUMMARY.format(total=round(total_value, 2), table=table_str)


async def send_profile_empty_message(message: Message, state: FSMContext):
    await send_one_message(
        message,
        state,
        text=PROFILE_EMPTY,
        reply_markup=create_profile_inline()
    )
