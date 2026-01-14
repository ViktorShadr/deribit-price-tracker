from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas.price import PriceOut, Ticker
from app.services.prices_service import PriceService

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("", response_model=list[PriceOut])
def read_prices(
    ticker: Ticker = Query(..., description="Тикер: btc_usd или eth_usd"), 
    db: Session = Depends(get_db)
):
    """
        Получить все сохранённые значения цены для указанного тикера.

        Query params:
          - ticker: обязательный (btc_usd / eth_usd)
    """
    service = PriceService(db)
    return service.get_all(ticker.value)


@router.get("/latest", response_model=PriceOut)
def read_latest_price(
    ticker: Ticker = Query(..., description="Тикер: btc_usd или eth_usd"), 
    db: Session = Depends(get_db)
):
    """
    Получить последнюю (самую свежую) цену для указанного тикера.

    Возвращает 404, если по тикеру нет данных.
    """
    service = PriceService(db)
    item = service.get_latest(ticker.value)
    if not item:
        raise HTTPException(status_code=404, detail="No data for this ticker")
    return item


@router.get("/by-date", response_model=list[PriceOut])
def read_prices_by_date(
    ticker: Ticker = Query(..., description="Тикер: btc_usd или eth_usd"),
    from_ts: int = Query(..., ge=0, description="Начальный timestamp (UNIX)"),
    to_ts: int = Query(..., ge=0, description="Конечный timestamp (UNIX)"),
    db: Session = Depends(get_db),
):
    """
        Получить цены по тикеру в диапазоне времени [from_ts, to_ts] (UNIX timestamp).

        Возвращает 400, если from_ts > to_ts.
    """
    if from_ts > to_ts:
        raise HTTPException(status_code=400, detail="from_ts must be <= to_ts")

    service = PriceService(db)
    return service.get_by_date(ticker.value, from_ts, to_ts)
