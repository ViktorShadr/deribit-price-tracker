from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


def create_db_engine() -> Engine:
    """
        Создаёт SQLAlchemy Engine на основе настроек проекта.

        Вынесено в фабрику, чтобы упростить тестирование и конфигурирование.
    """
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


def create_session_factory() -> sessionmaker:
    """
        Создаёт фабрику SQLAlchemy Session (sessionmaker) поверх Engine.
    """
    engine = create_db_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
