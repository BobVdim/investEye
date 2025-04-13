from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core.forms.share_price_form import ShareForm
from core.services.tinkoff_services import TinkoffService
from core.utils.logger import logger
from core.texts.share_price_texts import ENTER_TICKER, ERROR, NOT_FOUND, PRICE_RESPONSE


class SharePriceHandler:
    def __init__(self, service: TinkoffService):
        self.service = service

    async def get_price(self, message: Message, state: FSMContext):
        try:
            await self._clean_chat(message)

            msg = await message.answer(
                ENTER_TICKER.format(name=message.from_user.first_name),
                parse_mode='HTML'
            )

            await self._set_state(state, msg.message_id)

        except Exception:
            logger.exception("Ошибка в get_price")
            await self._send_response(message, ERROR)

    async def get_answer(self, message: Message, state: FSMContext):
        try:
            await self._clean_chat(message)
            await self._delete_old_bot_message(message, state)

            ticker = await self._validate_ticker(message)
            if not ticker:
                return

            await self._price_response(message, ticker)

        except Exception:
            logger.exception("Ошибка в get_answer")
            await self._send_response(message, ERROR)
        finally:
            await state.clear()

    async def _price_response(self, message: Message, ticker: str):
        price = self.service.get_share_price(ticker)

        if price:
            await self._send_response(
                message,
                PRICE_RESPONSE.format(ticker=ticker, price=price),
                parse_mode='HTML'
            )
        else:
            await self._send_response(
                message,
                NOT_FOUND.format(ticker=ticker),
                parse_mode='HTML'
            )

    @staticmethod
    async def _validate_ticker(message: Message):
        ticker = message.text.strip().upper()
        if not ticker:
            await message.answer(EMPTY_TICKER)
            return None
        return ticker

    @staticmethod
    async def _send_response(message: Message, text_: str, parse_mode: str = 'HTML'):
        try:
            await message.answer(text_, parse_mode=parse_mode)
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")

    @staticmethod
    async def _clean_chat(message: Message):
        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение пользователя: {e}")

    @staticmethod
    async def _set_state(state: FSMContext, msg_id: int):
        await state.update_data(msg_id=msg_id)
        await state.set_state(ShareForm.GET_TICKER)

    @staticmethod
    async def _delete_old_bot_message(message: Message, state: FSMContext):
        data = await state.get_data()
        msg_id = data.get("msg_id")
        if msg_id:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                logger.warning("Не удалось удалить старое сообщение бота")
