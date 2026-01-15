from enum import Enum

VALID_TICKERS: tuple[str, ...] = ("btc_usd", "eth_usd")


class Ticker(str, Enum):
    """Валидные тикеры для API и базы."""

    BTC_USD = "btc_usd"
    ETH_USD = "eth_usd"
