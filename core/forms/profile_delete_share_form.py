from aiogram.fsm.state import State, StatesGroup


class ProfileDeleteShare(StatesGroup):
    DELETE_SHARE = State()
    DELETE_COUNT = State()
