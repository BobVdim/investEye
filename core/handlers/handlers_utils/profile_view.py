from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from core.keyboards.reply import add_share_button
from core.services.profile_service import get_user_profile_from_db, get_portfolio_current_value
from core.handlers.handlers_utils.share_price_utils import clean_chat, send_one_message, delete_previous_bot_message
from core.keyboards.inline import create_profile_inline
from core.services.stock_service import StockService
from core.utils.logger import logger
from core.texts.profile_texts import PROFILE_EMPTY
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

        stock_service = StockService()
        current_value = get_portfolio_current_value(user_id, stock_service)

        if view_mode == "mobile":
            text = build_profile_text_mobile(profile_data, current_value)
        else:
            text = build_profile_text_pc(profile_data, current_value)

        await send_one_message(
            message,
            state,
            text=text,
            reply_markup=add_share_button
        )

    except Exception:
        logger.exception("Ошибка в get_user_profile_message")
        await send_one_message(message, state, text=ERROR_GET_PROFILE)


def build_profile_text_pc(rows: list[tuple], current_value: float = None) -> str:
    total_spent = 0
    table_lines = []
    share_performance = []

    header = (
        "┌────────────┬──────────────┬────────────┬──────────────┬──────────────┐\n"
        "│ Акция      │ Цена (₽)     │ Кол-во     │ Затраты (₽)  │ Текущая (₽) │\n"
        "├────────────┼──────────────┼────────────┼──────────────┼──────────────┤"
    )
    table_lines.append(header)

    for share, price, count in rows:
        if price is None or count is None:
            continue

        spent = round(price * count, 2)
        total_spent += spent

        current_price_data = StockService().get_share_price(share)
        current_price = current_price_data["rub"] if current_price_data else price
        current_value = round(current_price * count, 2)

        performance = (current_price - price) / price * 100
        share_performance.append((share, performance))

        formatted_price = f"{price:,.2f}".replace(",", " ").replace(".", ",")
        formatted_count = f"{count:,}".replace(",", " ")
        formatted_spent = f"{spent:,.2f}".replace(",", " ").replace(".", ",")
        formatted_current = f"{current_value:,.2f}".replace(",", " ").replace(".", ",")

        line = (
            f"│ {share.upper():<10} │"
            f" {formatted_price:>12} │"
            f" {formatted_count:>10} │"
            f" {formatted_spent:>12} │"
            f" {formatted_current:>12} │"
        )
        table_lines.append(line)
        table_lines.append("├────────────┼──────────────┼────────────┼──────────────┼──────────────┤")

    if len(table_lines) > 1:
        table_lines.pop()

    table_lines.append("└────────────┴──────────────┴────────────┴──────────────┴──────────────┘")

    table_str = "\n".join(table_lines)
    formatted_spent = f"{total_spent:,.2f}".replace(",", " ").replace(".", ",")
    formatted_current = f"{current_value:,.2f}".replace(",", " ").replace(".", ",")

    difference = current_value - total_spent
    if difference < 0:
        difference_text = f"📉 Упал на {abs(difference):,.2f} ₽ ({abs(difference / total_spent * 100):,.2f}%)"
    else:
        difference_text = f"📈 Вырос на {difference:,.2f} ₽ ({difference / total_spent * 100:,.2f}%)"

    if share_performance:
        if len(share_performance) == 1:
            share, perf = share_performance[0]
            if perf >= 0:
                performance_text = f"\n\n- 📈 <b>Лучшая акция:</b> {share.upper()} (+{perf:.2f}%)"
            else:
                performance_text = f"\n\n- 📉 <b>Худшая акция:</b> {share.upper()} ({perf:.2f}%)"
        else:
            worst_share, worst_perf = min(share_performance, key=lambda x: x[1])
            best_share, best_perf = max(share_performance, key=lambda x: x[1])
            performance_text = (
                f"\n\n- 📈 <b>Лучшая акция:</b> {best_share.upper()} (+{best_perf:.2f}%)\n"
                f"- 📉 <b>Худшая акция:</b> {worst_share.upper()} ({worst_perf:.2f}%)"
            )
    else:
        performance_text = ""

    return (
        f"💼 <b>Общая стоимость портфеля:</b>\n"
        f"- <i>Затраты:</i> <b>{formatted_spent} ₽</b>\n"
        f"- <i>Текущая:</i> <b>{formatted_current} ₽</b>\n"
        f"- {difference_text}"
        f"{performance_text}\n\n"
        f"<pre>{table_str}</pre>"
    )


def build_profile_text_mobile(rows: list, current_value: float = None) -> str:
    total_spent = 0
    total_current = current_value if current_value is not None else 0
    lines = []
    share_performance = []

    for share, price, count in rows:
        if price is None or count is None:
            continue

        spent = round(price * count, 2)
        total_spent += spent

        current_price_data = StockService().get_share_price(share)
        current_price = current_price_data["rub"] if current_price_data else price
        share_current_value = round(current_price * count, 2)
        if current_value is None:
            total_current += share_current_value

        performance = (current_price - price) / price * 100
        share_performance.append((share, performance))

        formatted_price = f"{price:,.2f}".replace(",", " ").replace(".", ",")
        formatted_count = f"{count:,}".replace(",", " ")

        lines.append(
            f"📊 <b>{share.upper()}</b>\n"
            f"💰 <i>Цена покупки:</i> {formatted_price} ₽\n"
            f"🛒 <i>Кол-во:</i> {formatted_count}\n"
            f"📈 <i>Изменение:</i> {performance:+.2f}%\n"
        )

    formatted_spent = f"{total_spent:,.2f}".replace(",", " ").replace(".", ",")
    formatted_current = f"{total_current:,.2f}".replace(",", " ").replace(".", ",")

    difference = total_current - total_spent
    if difference < 0:
        difference_text = f"📉 Упал на {abs(difference):,.2f} ₽ ({abs(difference / total_spent * 100):,.2f}%)"
    else:
        difference_text = f"📈 Вырос на {difference:,.2f} ₽ ({difference / total_spent * 100:,.2f}%)"

    if share_performance:
        if len(share_performance) == 1:
            share, perf = share_performance[0]
            if perf >= 0:
                performance_text = f"\n\n📈 <b>Лучшая акция:</b> {share.upper()} (+{perf:.2f}%)"
            else:
                performance_text = f"\n\n📉 <b>Худшая акция:</b> {share.upper()} ({perf:.2f}%)"
        else:
            worst_share, worst_perf = min(share_performance, key=lambda x: x[1])
            best_share, best_perf = max(share_performance, key=lambda x: x[1])
            performance_text = (
                f"\n\n📈 <b>Лучшая акция:</b> {best_share.upper()} (+{best_perf:.2f}%)\n"
                f"📉 <b>Худшая акция:</b> {worst_share.upper()} ({worst_perf:.2f}%)"
            )
    else:
        performance_text = ""

    return (
            f"💼 <b>Общая стоимость портфеля:</b>\n"
            f"- <i>Затраты:</i> <b>{formatted_spent} ₽</b>\n"
            f"- <i>Текущая:</i> <b>{formatted_current} ₽</b>\n"
            f"- {difference_text}"
            f"{performance_text}\n\n"
            + "\n".join(lines)
    )


async def send_profile_empty_message(message: Message, state: FSMContext):
    await send_one_message(
        message,
        state,
        text=PROFILE_EMPTY,
        reply_markup=create_profile_inline()
    )
