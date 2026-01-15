from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.tickers import VALID_TICKERS
from app.db.base import Base


class Price(Base):
    """ORM-модель сохранённых цен (index price) по тикерам Deribit."""

    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    ticker: Mapped[str] = mapped_column(String(16), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)

    ts: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (
        Index("uq_prices_ticker_ts", "ticker", "ts", unique=True),
        # Валидация тикеров на уровне БД
        CheckConstraint(
            f"ticker IN ({', '.join(repr(t) for t in VALID_TICKERS)})",
            name="check_valid_ticker",
        ),
    )
