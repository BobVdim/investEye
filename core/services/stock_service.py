import requests
import yfinance as yf

from core.utils.logger import logger


class StockService:
    @staticmethod
    def get_share_price(ticker: str):

        """
        Получаем цену акции и возвращаем её в рублях и долларах
        """

        usd_rub = StockService.get_usd_rub_rate()
        if usd_rub is None:
            logger.warning("Не удалось получить курс USD/RUB")
            return None

        # Сначала пробуем получить цену с MOEX (в рублях)
        moex_price = StockService._get_moex_price(ticker)
        if moex_price is not None:
            return {
                "rub": moex_price,
                "usd": moex_price / usd_rub
            }

        # Если не удалось — пробуем через Yahoo (в долларах)
        yahoo_price = StockService._get_yahoo_price(ticker)
        if yahoo_price is not None:
            return {
                "usd": yahoo_price,
                "rub": yahoo_price * usd_rub
            }

        return None

    @staticmethod
    def _get_moex_price(ticker: str):

        """
        Получаем цену акций российских компаний (в рублях) с MOEX
        """

        url = (f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/"
               f"securities/{ticker}.jsonp?iss.meta=off&iss.json=extended")

        try:
            response = requests.get(url)
            if response.status_code == 200:
                json_data = response.json()

                if 'marketdata' in json_data[1] and json_data[1]['marketdata']:
                    last_price = json_data[1]['marketdata'][0].get('LAST')
                    if last_price:
                        return last_price

                if 'securities' in json_data[1] and json_data[1]['securities']:
                    prev_price = json_data[1]['securities'][0].get('PREVPRICE')
                    if prev_price:
                        return prev_price

                logger.info(f'Нет доступных данных по тикеру {ticker} на MOEX')
                return None
            else:
                logger.warning(f"Ошибка при запросе MOEX: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Ошибка при получении данных с MOEX для {ticker}: {e}")
            return None

    @staticmethod
    def _get_yahoo_price(ticker: str):

        """
        Получаем цену акций иностранных компаний (в долларах) через Yahoo Finance
        """

        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")

            if not data.empty:
                price = data["Close"].iloc[-1]
                return price
            else:
                logger.warning(f"Данные по {ticker} не найдены через Yahoo")
                return None

        except Exception as e:
            logger.error(f"Ошибка при получении данных с Yahoo для {ticker}: {e}")
            return None

    @staticmethod
    def get_usd_rub_rate():

        """
        Получаем текущий курс доллара к рублю с сайта ЦБ РФ
        """
        
        try:
            response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
            if response.status_code == 200:
                data = response.json()
                return data["Valute"]["USD"]["Value"]
            else:
                logger.warning(f"Ошибка при получении курса USD/RUB: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Ошибка при получении курса USD/RUB: {e}")
            return None
