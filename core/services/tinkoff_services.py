from tinkoff.invest import Client
from tinkoff.invest.utils import quotation_to_decimal
from core.utils.logger import logger
from settings import API_KEY


class TinkoffService:
    def __init__(self, token: str = API_KEY):
        self.token = token

    def get_share_price(self, ticker: str):
        with Client(self.token) as client:
            try:
                instrument = self.find_share(client, ticker)
                if not instrument:
                    logger.warning(f"Share with ticker {ticker} not found")
                    return None

                last_price = self.get_last_price(client, instrument.figi)
                return quotation_to_decimal(last_price)

            except Exception:
                logger.exception(f"Error getting price for {ticker}")
                return None

    @staticmethod
    def find_share(client, ticker: str):
        instruments = client.instruments.find_instrument(query=ticker).instruments
        for instrument in instruments:
            if (instrument.ticker == ticker.upper() and
                    instrument.instrument_type == "share"):
                return instrument
        return None

    @staticmethod
    def get_last_price(client, figi: str):
        return client.market_data.get_last_prices(figi=[figi]).last_prices[0].price
