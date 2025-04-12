from environs import Env
from dataclasses import dataclass


@dataclass
class TelegramBot:
    bot_token: str


@dataclass
class TinkoffInvest:
    api_key: str


@dataclass
class Bots:
    telegram_bot: TelegramBot
    tinkoff_invest: TinkoffInvest


@dataclass
class Settings:
    bots: Bots


def get_settings(path: str):
    env = Env()
    env.read_env(path)

    telegram_token = env.str("TELEGRAM_TOKEN")
    tinkoff_api_key = env.str("TINKOFF_INVEST_KEY")

    return Settings(
        bots=Bots(
            telegram_bot=TelegramBot(bot_token=telegram_token),
            tinkoff_invest=TinkoffInvest(api_key=tinkoff_api_key),
        )
    )


settings = get_settings('envfile')

API_KEY = settings.bots.tinkoff_invest.api_key
TOKEN = settings.bots.telegram_bot.bot_token
