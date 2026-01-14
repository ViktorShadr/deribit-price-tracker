from sqlalchemy import BigInteger, Numeric, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Price(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    ticker: Mapped[str] = mapped_column(String(16), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)

    ts: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (
        Index("ix_prices_ticker_ts", "ticker", "ts"),
    )
