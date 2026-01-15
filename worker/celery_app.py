"""
Celery application для периодической загрузки цен индексов.
"""

from functools import lru_cache

from celery import Celery

from app.core.config import get_settings


def _build_celery_app() -> Celery:
    settings = get_settings()
    app = Celery(
        "deribit_price_tracker",
        broker=settings.celery_broker_url,
        backend=settings.celery_backend_url,
        include=["worker.tasks"],
    )
    app.conf.timezone = "UTC"
    app.conf.beat_schedule = {
        "fetch-index-prices-every-minute": {
            "task": "worker.tasks.fetch_and_store_prices",
            "schedule": 60.0,
        }
    }
    return app


@lru_cache(maxsize=1)
def get_celery_app() -> Celery:
    return _build_celery_app()
