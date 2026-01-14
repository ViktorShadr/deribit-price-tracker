import time
from decimal import Decimal

from worker.celery_app import celery_app
from app.services.deribit_client import DeribitClient
from app.db.session import SessionLocal
from app.db.crud import save_prices

TICKERS = ["btc_usd", "eth_usd"]

@celery_app.task(name="worker.tasks.fetch_and_store_prices")
def fetch_and_store_prices():
    ts = int(time.time())
    prices = DeribitClient().get_index_prices(TICKERS)

    # пишем в БД
    session = SessionLocal()
    try:
        save_prices(session, prices, ts)
        session.commit()
    finally:
        session.close()

    return {"ts": ts, "prices": prices}
