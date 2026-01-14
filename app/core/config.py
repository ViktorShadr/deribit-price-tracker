from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    database_url: str
    celery_broker_url: str
    celery_backend_url: str
    deribit_base_url: str
    tickers: tuple[str, ...]


def _parse_csv(value: str) -> tuple[str, ...]:
    items = [x.strip() for x in value.split(",")]
    return tuple(x for x in items if x)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Единая точка чтения конфигурации.
    """
    load_dotenv(BASE_DIR / ".env")

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Put it into .env or environment variables."
        )

    tickers_raw = os.getenv("TICKERS", "btc_usd,eth_usd")
    tickers = _parse_csv(tickers_raw)
    if not tickers:
        raise RuntimeError("TICKERS is empty. Example: TICKERS=btc_usd,eth_usd")

    return Settings(
        database_url=database_url,
        celery_broker_url=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        celery_backend_url=os.getenv("CELERY_BACKEND_URL", "redis://localhost:6379/1"),
        deribit_base_url=os.getenv("DERIBIT_BASE_URL", "https://www.deribit.com/api/v2"),
        tickers=tickers,
    )

