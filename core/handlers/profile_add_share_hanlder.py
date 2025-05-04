from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.forms.profile_form import ProfileForm
from core.handlers.profile_view import build_profile_text
from core.keyboards.reply import add_share_button
from core.services.profile_service import get_user_profile_from_db, save_share_to_db
from core.handlers.handlers_utils.share_price_utils import send_one_message
from core.handlers.handlers_utils.share_price_utils import delete_previous_bot_message, clean_chat


async def add_share_handler(message: Message, state: FSMContext):
    await delete_previous_bot_message(message, state)
    await clean_chat(message)

    user_id = message.from_user.id
    profile_data = get_user_profile_from_db(user_id)

    if profile_data:
        await send_one_message(
            message,
            state,
            text="Введите тикер акции:"
        )
        await state.set_state(ProfileForm.ADD_SHARE)
    else:
        await send_one_message(
            message,
            state,
            text="❌ У вас нет профиля. Пожалуйста, создайте профиль сначала."
        )


async def process_add_share(message: Message, state: FSMContext):
    await delete_previous_bot_message(message, state)
    await clean_chat(message)

    share_ticker = message.text.strip()
    await state.update_data(share=share_ticker)

    await send_one_message(
        message,
        state,
        text="Введите цену акции:"
    )
    await state.set_state(ProfileForm.ADD_PRICE)


async def process_add_price(message: Message, state: FSMContext):
    await delete_previous_bot_message(message, state)
    await clean_chat(message)

    try:
        price = float(message.text.strip())
        await state.update_data(price=price)

        await send_one_message(
            message,
            state,
            text="Введите количество акций:"
        )
        await state.set_state(ProfileForm.ADD_COUNT)
    except ValueError:
        await send_one_message(
            message,
            state,
            text="❌ Пожалуйста, введите корректную цену."
        )


async def process_add_count(message: Message, state: FSMContext):
    try:
        await delete_previous_bot_message(message, state)
        await clean_chat(message)

        count = int(message.text.strip())
        await state.update_data(count=count)

        user_data = await state.get_data()
        share_ticker = user_data["share"]
        price = user_data["price"]
        count = user_data["count"]

        user_id = message.from_user.id
        save_share_to_db(user_id, share_ticker, price, count)

        profile_data = get_user_profile_from_db(user_id)
        text = build_profile_text(profile_data)

        await send_one_message(
            message,
            state,
            text=(
                f"{text}"
            ),
            reply_markup=add_share_button
        )
    except ValueError:
        await send_one_message(
            message,
            state,
            text="❌ Пожалуйста, введите корректное количество."
        )
