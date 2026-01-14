from __future__ import annotations

from decimal import Decimal
from typing import Mapping

from sqlalchemy.orm import Session

from app.db.models import Price


def save_price(session: Session, ticker: str, price: Decimal, ts: int) -> None:
    row = Price(ticker=ticker, price=price, ts=ts)
    session.add(row)


def save_prices(session: Session, prices: Mapping[str, Decimal], ts: int) -> int:
    """
    Сохраняет пачку цен за один timestamp.
    Возвращает количество добавленных строк.
    """
    for ticker, price in prices.items():
        save_price(session, ticker=ticker, price=price, ts=ts)

    return len(prices)


def get_prices(db: Session, ticker: str) -> list[Price]:
    return (
        db.query(Price)
        .filter(Price.ticker == ticker)
        .order_by(Price.ts.asc())
        .all()
    )


def get_latest_price(db: Session, ticker: str) -> Price | None:
    return (
        db.query(Price)
        .filter(Price.ticker == ticker)
        .order_by(Price.ts.desc())
        .first()
    )


def get_prices_by_date(db: Session, ticker: str, from_ts: int, to_ts: int) -> list[Price]:
    return (
        db.query(Price)
        .filter(
            Price.ticker == ticker,
            Price.ts >= from_ts,
            Price.ts <= to_ts,
        )
        .order_by(Price.ts.asc())
        .all()
    )
