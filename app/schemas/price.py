from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, field_validator


class Ticker(str, Enum):
    """Валидные тикеры для API."""
    BTC_USD = "btc_usd"
    ETH_USD = "eth_usd"


class PriceOut(BaseModel):
    """Pydantic-модель для сериализации цены."""

    ticker: str
    price: Decimal
    ts: int

    class Config:
        from_attributes = True


class TickerQuery(BaseModel):
    """Валидация query параметра ticker."""
    
    ticker: Ticker

    class Config:
        extra = "forbid"  # Запрещаем дополнительные поля
