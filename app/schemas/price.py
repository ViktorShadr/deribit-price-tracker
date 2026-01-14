from decimal import Decimal

from pydantic import BaseModel


class PriceOut(BaseModel):
    ticker: str
    price: Decimal
    ts: int

    class Config:
        from_attributes = True
