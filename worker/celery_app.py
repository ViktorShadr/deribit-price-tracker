"""
   Celery application для периодической загрузки цен индексов.
"""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "deribit_price_tracker",
    broker=settings.celery_broker_url,
    backend=settings.celery_backend_url,
    include=["worker.tasks"],
)

celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "fetch-index-prices-every-minute": {
        "task": "worker.tasks.fetch_and_store_prices",
        "schedule": 60.0,
    }
}
