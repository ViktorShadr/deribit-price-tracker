from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.crud import get_prices, get_latest_price, get_prices_by_date
from app.schemas.price import PriceOut

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("", response_model=list[PriceOut])
def read_prices(ticker: str = Query(...), db: Session = Depends(get_db)):
    return get_prices(db, ticker)

@router.get("/latest", response_model=PriceOut)
def read_latest_price(ticker: str = Query(...), db: Session = Depends(get_db)):
    item = get_latest_price(db, ticker)
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
    return get_prices_by_date(db, ticker, from_ts, to_ts)
