from aiogram.fsm.state import State, StatesGroup


class ProfileViewMode(StatesGroup):
    PC_VIEW = State()
    MOBILE_VIEW = State()
