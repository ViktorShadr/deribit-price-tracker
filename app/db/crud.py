from __future__ import annotations

from decimal import Decimal
from typing import Mapping

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.models import Price


def save_price(session: Session, ticker: str, price: Decimal, ts: int) -> bool:
    """
    Сохраняет цену в БД с обработкой дубликатов.

    Returns:
        bool: True если сохранено, False если дубликат
    """
    stmt = (
        insert(Price)
        .values(ticker=ticker, price=price, ts=ts)
        .on_conflict_do_nothing(index_elements=["ticker", "ts"])
    )
    result = session.execute(stmt)
    return result.rowcount == 1


def save_prices(session: Session, prices: Mapping[str, Decimal], ts: int) -> int:
    """
    Сохраняет пачку цен за один timestamp с обработкой дубликатов.
    Возвращает количество успешно добавленных строк.
    """
    if not prices:
        return 0

    rows = [{"ticker": ticker, "price": price, "ts": ts} for ticker, price in prices.items()]
    stmt = insert(Price).values(rows).on_conflict_do_nothing(
        index_elements=["ticker", "ts"]
    )
    result = session.execute(stmt)
    return result.rowcount or 0


def get_prices(db: Session, ticker: str) -> list[Price]:
    return db.query(Price).filter(Price.ticker == ticker).order_by(Price.ts.asc()).all()


def get_latest_price(db: Session, ticker: str) -> Price | None:
    return (
        db.query(Price).filter(Price.ticker == ticker).order_by(Price.ts.desc()).first()
    )


def get_prices_by_date(
    db: Session, ticker: str, from_ts: int, to_ts: int
) -> list[Price]:
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
