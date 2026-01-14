import time

from app.core.config import get_settings
from app.db.crud import save_prices
from app.db.deps import SessionLocal
from app.services.deribit_client import DeribitClient, DeribitError
from worker.celery_app import celery_app

settings = get_settings()


@celery_app.task(
    name="worker.tasks.fetch_and_store_prices",
    autoretry_for=(DeribitError,),
    retry_kwargs={"max_retries": 5},
    retry_backoff=True,
    retry_jitter=True,
)
def fetch_and_store_prices():
    """
        Celery task: раз в минуту получает index price по тикерам и сохраняет в БД.

        Сохраняет:
          - ticker
          - price
          - ts (UNIX timestamp, seconds)
    """
    ts = int(time.time())

    client = DeribitClient(base_url=settings.deribit_base_url)
    prices = client.get_index_prices(settings.tickers)

    session = SessionLocal()
    try:
        save_prices(session, prices, ts)
        session.commit()
    finally:
        session.close()

    return {"ts": ts, "prices": prices}
