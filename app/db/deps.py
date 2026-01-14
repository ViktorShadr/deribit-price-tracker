from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import create_session_factory

SessionLocal = create_session_factory()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
