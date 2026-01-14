from pydantic import BaseModel


class PriceOut(BaseModel):
    ticker: str
    price: float
    ts: int

    class Config:
        from_attributes = True
