from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from tinkoff.invest import Client
from tinkoff.invest.utils import quotation_to_decimal

from core.forms.share_price_form import ShareForm
from settings import API_KEY

TOKEN = API_KEY


def share_price_by_ticker(ticker: str):
    with Client(TOKEN) as client:
        try:
            instruments = client.instruments.find_instrument(query=ticker)

            for instrument in instruments.instruments:
                if instrument.ticker == ticker.upper() and instrument.instrument_type == "share":
                    figi = instrument.figi
                    last_price = client.market_data.get_last_prices(figi=[figi]).last_prices[0].price
                    return quotation_to_decimal(last_price)

            return None

        except Exception as e:
            print(f"Ошибка при получении цены для {ticker}: {e}")
            return None


async def get_price(message: Message, state: FSMContext):
    try:
        await message.delete()

        msg = await message.answer(
            f"{message.from_user.first_name}, введите тикер акции\n"
            f"Например: <code>AAPL</code> или <code>SBER</code>",
            parse_mode='HTML'
        )

        await state.update_data(msg_id=msg.message_id)
        await state.set_state(ShareForm.GET_TICKER)

    except Exception as e:
        print(f"Ошибка в функции get_price: {e}")
        await message.answer("❌ Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже.")


async def get_answer_about_price(message: Message, state: FSMContext):
    try:
        await message.delete()

        data = await state.get_data()
        msg_id = data.get("msg_id")
        if msg_id:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение бота: {e}")

        ticker = message.text.strip().upper()

        if not ticker:
            await message.answer('❌ Вы не ввели тикер. Пожалуйста, попробуйте снова!')
            return

        price = share_price_by_ticker(ticker)

        if price:
            await message.answer(
                f"📊 <b>{ticker}</b>\n\nТекущая цена: <code>{price:.2f}</code> USD",
                parse_mode='HTML')
        else:
            await message.answer(
                f"❌ Не удалось найти акцию с тикером <code>{ticker}</code>\n"
                f"Проверь правильность ввода и попробуй снова.",
                parse_mode='HTML'
            )

    except Exception as e:
        print(f"Ошибка в функции get_answer_about_price: {e}")
        await message.answer("❌ Произошла ошибка. Попробуй позже.")
    finally:
        await state.clear()
