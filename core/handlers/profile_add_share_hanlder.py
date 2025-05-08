from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.forms.profile_add_share_form import ProfileAddShare
from core.handlers.handlers_utils.profile_view import build_profile_text, send_profile_empty_message
from core.keyboards.reply import add_share_button
from core.services.profile_service import get_user_profile_from_db, save_share_to_db
from core.handlers.handlers_utils.share_price_utils import send_one_message
from core.handlers.handlers_utils.share_price_utils import delete_previous_bot_message, clean_chat

from core.texts import profile_texts


async def add_share_handler(message: Message, state: FSMContext):
    await delete_previous_bot_message(message, state)
    await clean_chat(message)

    user_id = message.from_user.id
    profile_data = get_user_profile_from_db(user_id)

    if profile_data:
        await send_one_message(message, state, text=profile_texts.ENTER_TICKER)
        await state.set_state(ProfileAddShare.ADD_SHARE)
    else:
        await send_profile_empty_message(message, state)


async def process_add_share(message: Message, state: FSMContext):
    await delete_previous_bot_message(message, state)
    await clean_chat(message)

    share_ticker = message.text.strip().upper()

    if not is_valid_ticker(share_ticker):
        await send_one_message(message, state, text=profile_texts.INVALID_TICKER)
        await state.set_state(ProfileAddShare.ADD_SHARE)
        return

    await state.update_data(share=share_ticker)
    await send_one_message(message, state, text=profile_texts.ENTER_PRICE)
    await state.set_state(ProfileAddShare.ADD_PRICE)


async def process_add_price(message: Message, state: FSMContext):
    await delete_previous_bot_message(message, state)
    await clean_chat(message)

    user_data = await state.get_data()
    share_ticker = user_data["share"]

    if message.text.strip() == "-":
        from core.services.stock_service import StockService
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
        await delete_previous_bot_message(message, state)
        await clean_chat(message)

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
        text = build_profile_text(profile_data)

        await send_one_message(message, state, text=text, reply_markup=add_share_button)
    except ValueError:
        await send_one_message(message, state, text=profile_texts.INVALID_COUNT)
        await state.set_state(ProfileAddShare.ADD_COUNT)


def is_valid_ticker(ticker: str) -> bool:
    if len(ticker) < 1 or len(ticker) > 5:
        return False
    if not ticker.isalnum():
        return False
    if ticker.isdigit():
        return False
    return True
