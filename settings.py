from environs import Env
from dataclasses import dataclass


@dataclass
class TelegramBot:
    bot_token: str


@dataclass
class ApiKeys:
    finnhub_api_key: str


@dataclass
class Bots:
    telegram_bot: TelegramBot


@dataclass
class Settings:
    bots: Bots
    api_keys: ApiKeys


def get_settings(path: str):
    env = Env()
    env.read_env(path)

    telegram_token = env.str("TELEGRAM_TOKEN")
    finnhub_key = env.str("FINNHUB_API_KEY")

    return Settings(
        bots=Bots(
            telegram_bot=TelegramBot(bot_token=telegram_token),
        ),
        api_keys=ApiKeys(
            finnhub_api_key=finnhub_key,
        )
    )


settings = get_settings("envfile")
