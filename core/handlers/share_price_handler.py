from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.services.stock_service import StockService
from core.utils.logger import logger
from core.texts.share_price_texts import ENTER_TICKER, NOT_FOUND, PRICE_RESPONSE
from core.texts.errors_texts import ERROR
from core.handlers.handlers_utils.share_price_utils import (
    clean_chat,
    send_one_message,
    delete_previous_bot_message,
)
from core.keyboards.inline import create_repeat_share_inline
from core.validators.ticker_validator import validate_ticker
from core.forms.share_price_form import ShareForm


class SharePriceHandler:
    def __init__(self, service: StockService):
        self.service = service

    @staticmethod
    async def get_price(message: Message, state: FSMContext):
        """
        Первый шаг — просим ввести тикер. Стираем сообщение пользователя.
        Отправляем боту новое сообщение и сохраняем его ID.
        """
        try:
            await delete_previous_bot_message(message, state)
            await state.set_state(None)
            await clean_chat(message)

            await send_one_message(
                message,
                state,
                text=ENTER_TICKER.format(name=message.from_user.first_name),
                reply_markup=None
            )

            await state.set_state(ShareForm.GET_TICKER)

        except Exception:
            logger.exception("Ошибка в get_price")
            await send_one_message(message, state, ERROR)

    async def get_answer(self, message: Message, state: FSMContext):

        """
        Второй шаг — получаем тикер от пользователя, валидируем, получаем цену.
        """

        try:
            await clean_chat(message)

            ticker = await validate_ticker(message)
            if not ticker:
                return

            await self._price_response(message, state, ticker)

        except Exception:
            logger.exception("Ошибка в get_answer")
            await send_one_message(message, state, ERROR)

    async def _price_response(self, message: Message, state: FSMContext, ticker: str):

        """
        Отправка ответа с ценой акции (или сообщение об ошибке).
        """

        price = self.service.get_share_price(ticker)

        if price:
            text = PRICE_RESPONSE.format(ticker=ticker, price_rub=round(price['rub'], 2),
                                         price_usd=round(price['usd'], 2))

        else:
            text = NOT_FOUND.format(ticker=ticker)

        await send_one_message(
            message,
            state,
            text=text,
            reply_markup=create_repeat_share_inline()
        )
