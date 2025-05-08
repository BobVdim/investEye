from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


class ResetStateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message) and not isinstance(event, CallbackQuery):
            state: FSMContext = data.get("state")
            if state:
                current_state = await state.get_state()
                if current_state and event.text not in ["✨ Добавить акцию", "🗑️ Удалить акцию"]:
                    await state.set_state(None)

        return await handler(event, data)