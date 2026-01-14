from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import create_session_factory

SessionLocal = create_session_factory()


def get_db() -> Generator[Session, None, None]:
    """
        FastAPI dependency: предоставляет SQLAlchemy Session и гарантирует закрытие.

        Используется через Depends(get_db) в роутерах.
        """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
