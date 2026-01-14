from decimal import Decimal

from pydantic import BaseModel


class PriceOut(BaseModel):
    """Pydantic-модель для сериализации цены."""

    ticker: str
    price: Decimal
    ts: int

    class Config:
        from_attributes = True
