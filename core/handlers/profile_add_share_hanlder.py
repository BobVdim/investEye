from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.forms.profile_add_share_form import ProfileAddShare
from core.forms.profile_view_mode_form import ProfileViewMode
from core.services.profile_service import (
    get_user_profile_from_db,
    save_share_to_db
)
from core.services.stock_service import StockService
from core.handlers.handlers_utils.share_price_utils import (
    send_one_message,
    delete_previous_bot_message,
    clean_chat
)
from core.handlers.handlers_utils.profile_view import (
    build_profile_text_pc,
    build_profile_text_mobile,
    send_profile_empty_message
)
from core.keyboards.reply import add_share_button
from core.texts import profile_texts


async def add_share_handler(message: Message, state: FSMContext):
    await clean_chat(message)
    await delete_previous_bot_message(message, state)

    user_id = message.from_user.id
    profile_data = get_user_profile_from_db(user_id)

    data = await state.get_data()
    view_mode = data.get("view_mode", "pc")
    await state.update_data(view_mode=view_mode)

    if profile_data:
        await send_one_message(message, state, text=profile_texts.ENTER_TICKER)
        await state.set_state(ProfileAddShare.ADD_SHARE)
    else:
        await send_profile_empty_message(message, state)


async def process_add_share(message: Message, state: FSMContext):
    await clean_chat(message)
    await delete_previous_bot_message(message, state)

    share_ticker = message.text.strip().upper()

    if not is_valid_ticker(share_ticker):
        await send_one_message(message, state, text=profile_texts.INVALID_TICKER)
        await state.set_state(ProfileAddShare.ADD_SHARE)
        return

    await state.update_data(share=share_ticker)
    await send_one_message(message, state, text=profile_texts.ENTER_PRICE)
    await state.set_state(ProfileAddShare.ADD_PRICE)


async def process_add_price(message: Message, state: FSMContext):
    await clean_chat(message)
    await delete_previous_bot_message(message, state)

    user_data = await state.get_data()
    share_ticker = user_data["share"]

    if message.text.strip() == "-":
        service = StockService()
        price_data = service.get_share_price(share_ticker)

        if price_data is None:
            await send_one_message(
                message, state,
                text=profile_texts.FAILED_TO_GET_PRICE.format(ticker=share_ticker)
            )
            return

        price = price_data["rub"]
        await state.update_data(price=price)

        await send_one_message(
            message, state,
            text=profile_texts.CURRENT_PRICE_TEXT.format(ticker=share_ticker, price=price)
        )
        await state.set_state(ProfileAddShare.ADD_COUNT)
    else:
        try:
            price = float(message.text.strip())
            await state.update_data(price=price)
            await send_one_message(message, state, text=profile_texts.ENTER_COUNT)
            await state.set_state(ProfileAddShare.ADD_COUNT)
        except ValueError:
            await send_one_message(message, state, text=profile_texts.INVALID_PRICE)
            await state.set_state(ProfileAddShare.ADD_PRICE)


async def process_add_count(message: Message, state: FSMContext):
    try:
        await clean_chat(message)
        await delete_previous_bot_message(message, state)

        data = await state.get_data()
        view_mode = data.get("view_mode", "pc")

        count = int(message.text.strip())
        if count <= 0:
            raise ValueError

        await state.update_data(count=count)

        user_data = await state.get_data()
        share_ticker = user_data["share"]
        price = user_data["price"]
        count = user_data["count"]

        user_id = message.from_user.id
        save_share_to_db(user_id, share_ticker, price, count)

        profile_data = get_user_profile_from_db(user_id)

        if not profile_data:
            await send_profile_empty_message(message, state)
            return

        if view_mode == "mobile":
            text = build_profile_text_mobile(profile_data)
        else:
            text = build_profile_text_pc(profile_data)

        await state.set_state(ProfileViewMode.PC_VIEW if view_mode == "pc" else ProfileViewMode.MOBILE_VIEW)
        await send_one_message(message, state, text=text, reply_markup=add_share_button)
    except ValueError:
        await send_one_message(message, state, text=profile_texts.INVALID_COUNT)
        await state.set_state(ProfileAddShare.ADD_COUNT)


def is_valid_ticker(ticker: str):
    if len(ticker) < 1 or len(ticker) > 5:
        return False
    if not ticker.isalnum():
        return False
    if ticker.isdigit():
        return False
    return True
