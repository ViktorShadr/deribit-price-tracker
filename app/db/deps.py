from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
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


@contextmanager
def get_db_context():
    """
        Контекстный менеджер для использования в Celery задачах.
        Гарантирует правильное закрытие сессии.
        """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
