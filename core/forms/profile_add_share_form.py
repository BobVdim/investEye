from aiogram.fsm.state import State, StatesGroup


class ProfileAddShare(StatesGroup):
    ADD_SHARE = State()
    ADD_PRICE = State()
    ADD_COUNT = State()
