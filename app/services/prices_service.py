from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db import crud
from app.db.models import Price


@dataclass(frozen=True)
class PriceService:
    db: Session

    def get_all(self, ticker: str) -> list[Price]:
        return crud.get_prices(self.db, ticker)

    def get_latest(self, ticker: str) -> Price | None:
        return crud.get_latest_price(self.db, ticker)

    def get_by_date(self, ticker: str, from_ts: int, to_ts: int) -> list[Price]:
        return crud.get_prices_by_date(self.db, ticker, from_ts, to_ts)