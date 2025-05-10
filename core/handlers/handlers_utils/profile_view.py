from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from core.forms.profile_view_mode_form import ProfileViewMode
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

        data = await state.get_data()
        view_mode = data.get("view_mode", "pc")

        if view_mode == "mobile":
            text = build_profile_text_mobile(profile_data)
        else:
            text = build_profile_text_pc(profile_data)

        await send_one_message(
            message,
            state,
            text=text,
            reply_markup=add_share_button
        )

    except Exception:
        logger.exception("Ошибка в get_user_profile_message")
        await send_one_message(message, state, text=ERROR_GET_PROFILE)


def build_profile_text_pc(rows: list[tuple]) -> str:
    total_value = 0
    table_lines = []

    header = (
        "┌────────────┬──────────────┬────────────┬──────────────┐\n"
        "│ Акция      │ Цена (₽)     │ Кол-во     │ Сумма (₽)    │\n"
        "├────────────┼──────────────┼────────────┼──────────────┤"
    )
    table_lines.append(header)

    for share, price, count in rows:
        if price is None or count is None:
            continue

        total = round(price * count, 2)
        total_value += total

        formatted_price = f"{price:,.2f}".replace(",", " ").replace(".", ",")
        formatted_count = f"{count:,}".replace(",", " ")
        formatted_total = f"{total:,.2f}".replace(",", " ").replace(".", ",")

        line = (
            f"│ {share.upper():<10} │"
            f" {formatted_price:>12} │"
            f" {formatted_count:>10} │"
            f" {formatted_total:>12} │"
        )
        table_lines.append(line)
        table_lines.append("├────────────┼──────────────┼────────────┼──────────────┤")

    if len(table_lines) > 1:
        table_lines.pop()

    table_lines.append("└────────────┴──────────────┴────────────┴──────────────┘")

    table_str = "\n".join(table_lines)
    formatted_total = f"{total_value:,.2f}".replace(",", " ").replace(".", ",")

    return (
        f"💼 <b>Общая стоимость портфеля:</b> <b>{formatted_total} ₽</b>\n\n"
        f"<pre>{table_str}</pre>"
    )


def build_profile_text_mobile(rows: list[tuple]) -> str:
    total_value = 0
    lines = []

    for share, price, count in rows:
        if price is None or count is None:
            continue

        total = round(price * count, 2)
        total_value += total

        formatted_price = f"{price:,.2f}".replace(",", " ").replace(".", ",")
        formatted_count = f"{count:,}".replace(",", " ")
        formatted_total = f"{total:,.2f}".replace(",", " ").replace(".", ",")

        lines.append(
            f"📊 <b>{share.upper()}</b>\n"
            f"💰 <i>Цена:</i> {formatted_price} ₽\n"
            f"🛒 <i>Кол-во:</i> {formatted_count}\n"
            f"💵 <i>Сумма:</i> {formatted_total} ₽\n"
        )

    formatted_total = f"{total_value:,.2f}".replace(",", " ").replace(".", ",")

    return (
            f"💼 <b>Общая стоимость портфеля:</b> <b>{formatted_total} ₽</b>\n\n"
            + "\n".join(lines)
    )


async def send_profile_empty_message(message: Message, state: FSMContext):
    await send_one_message(
        message,
        state,
        text=PROFILE_EMPTY,
        reply_markup=create_profile_inline()
    )
