from decimal import Decimal
from pydantic import BaseModel

from app.core.tickers import Ticker


class PriceOut(BaseModel):
    """Pydantic-модель для сериализации цены."""

    ticker: str
    price: Decimal
    ts: int

    class Config:
        from_attributes = True
