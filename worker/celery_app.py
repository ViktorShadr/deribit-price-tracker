from celery import Celery
from app.core.config import CELERY_BROKER_URL, CELERY_BACKEND_URL

celery_app = Celery(
    "deribit_price_tracker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_BACKEND_URL,
    include=["worker.tasks"],
)

celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "fetch-index-prices-every-minute": {
        "task": "worker.tasks.fetch_and_store_prices",
        "schedule": 60.0,
    }
}
