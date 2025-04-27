from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.services.stock_service import StockService
from core.utils.logger import logger
from core.texts.share_price_texts import ENTER_TICKER, NOT_FOUND, PRICE_RESPONSE
from core.texts.errors_texts import ERROR
from core.handlers.handlers_utils.share_price_utils import (
    send_response,
    clean_chat,
    set_state,
    edit_old_bot_message
)
from core.validators.ticker_validator import validate_ticker


class SharePriceHandler:
    def __init__(self, service: StockService):
        self.service = service

    @staticmethod
    async def get_price(message: Message, state: FSMContext):

        """
        Первый шаг — запрашивает у пользователя тикер акции.
        Очищает чат и сохраняет сообщение бота в состоянии.
        """

        try:
            await clean_chat(message)

            msg = await message.answer(
                ENTER_TICKER.format(name=message.from_user.first_name),
                parse_mode='HTML'
            )

            await set_state(state, msg.message_id)
        except Exception:
            logger.exception("Произошла ошибка в функции get_price. Проверьте её!")
            await send_response(message, ERROR)

    async def get_answer(self, message: Message, state: FSMContext):

        """
        Второй шаг — получает тикер от пользователя, валидирует его,
        получает цену акции и отправляет ответ.
        """

        try:
            await clean_chat(message)

            ticker = await validate_ticker(message)
            if not ticker:
                return

            await self._price_response(message, state, ticker, edit=True)

        except Exception:
            logger.exception("Произошла ошибка в функции get_answer. Проверьте её!")
            await send_response(message, ERROR)
        finally:
            await state.clear()

    async def _price_response(self, message: Message, state: FSMContext, ticker: str, edit=False):

        """
        Отправляет сообщение с ценой акции, если она найдена.
        Иначе сообщает, что тикер не найден.
        """

        price = self.service.get_share_price(ticker)

        if price:
            text = PRICE_RESPONSE.format(ticker=ticker, price=price)
        else:
            text = NOT_FOUND.format(ticker=ticker)

        if edit:
            await edit_old_bot_message(message, state, text)
        else:
            await send_response(message, text)
