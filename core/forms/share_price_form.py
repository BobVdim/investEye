from aiogram.fsm.state import State, StatesGroup


class ShareForm(StatesGroup):
    GET_TICKER = State()

