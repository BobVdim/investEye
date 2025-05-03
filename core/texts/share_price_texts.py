""" Сообщения для пользователя вынесены в отдельный файл, чтобы было легче их редактировать.
    Они упорядочены по мере их появления в коде"""

ENTER_TICKER = (
    "{name}, введите тикер акции\n"
    "Например: <code>AAPL</code> или <code>SBER</code>"
)

PRICE_RESPONSE = (
    "📊 <b>{ticker}</b>\n\nТекущая цена:\n"
    "<code>{price_rub:.2f}</code> RUB\n"
    "<code>{price_usd:.2f}</code> USD"
)

NOT_FOUND = "❌ Не удалось найти акцию <code>{ticker}</code>. Проверьте тикер и попробуйте снова."
