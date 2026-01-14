from __future__ import annotations

from typing import Mapping

from sqlalchemy.orm import Session

from app.db.models import Price


def save_price(session: Session, ticker: str, price: float, ts: int) -> None:
    row = Price(ticker=ticker, price=price, ts=ts)
    session.add(row)


def save_prices(session: Session, prices: Mapping[str, float], ts: int) -> int:
    """
    Сохраняет пачку цен за один timestamp.
    Возвращает количество добавленных строк.
    """
    for ticker, price in prices.items():
        save_price(session, ticker=ticker, price=price, ts=ts)

    return len(prices)
