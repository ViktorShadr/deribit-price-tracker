from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas.price import PriceOut
from app.services.prices_service import PriceService

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("", response_model=list[PriceOut])
def read_prices(ticker: str = Query(...), db: Session = Depends(get_db)):
    service = PriceService(db)
    return service.get_all(ticker)


@router.get("/latest", response_model=PriceOut)
def read_latest_price(ticker: str = Query(...), db: Session = Depends(get_db)):
    service = PriceService(db)
    item = service.get_latest(ticker)
    if not item:
        raise HTTPException(status_code=404, detail="No data for this ticker")
    return item


@router.get("/by-date", response_model=list[PriceOut])
def read_prices_by_date(
    ticker: str = Query(...),
    from_ts: int = Query(..., ge=0),
    to_ts: int = Query(..., ge=0),
    db: Session = Depends(get_db),
):
    if from_ts > to_ts:
        raise HTTPException(status_code=400, detail="from_ts must be <= to_ts")

    service = PriceService(db)
    return service.get_by_date(ticker, from_ts, to_ts)
