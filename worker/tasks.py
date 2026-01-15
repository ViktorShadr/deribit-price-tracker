import logging
import time

from app.core.config import get_settings
from app.db.crud import save_prices
from app.db.deps import get_db_context
from app.services.deribit_client import DeribitClient, DeribitError
from worker.celery_app import celery_app

logger = logging.getLogger(__name__)
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
    logger.info(f"Starting price fetch task at timestamp {ts}")

    try:
        client = DeribitClient(base_url=settings.deribit_base_url)
        prices = client.get_index_prices(settings.tickers)

        logger.info(f"Fetched prices: {prices}")

        # Используем контекстный менеджер для правильной работы с сессией
        with get_db_context() as session:
            saved_count = save_prices(session, prices, ts)

        logger.info(
            f"Successfully saved {saved_count} prices out of {len(prices)} requested"
        )
        return {"ts": ts, "prices": prices, "saved_count": saved_count}

    except DeribitError as e:
        logger.error(f"Deribit API error: {e}")
        raise  # Celery автоматически обработает retry
    except Exception as e:
        logger.error(f"Unexpected error in price fetch task: {e}")
        raise
