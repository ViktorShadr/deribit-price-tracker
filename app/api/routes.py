from fastapi import APIRouter, Query, HTTPException

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/")
def get_prices(
    ticker: str = Query(..., description="Currency ticker, e.g. btc_usd")
):
    raise HTTPException(
        status_code=501,
        detail="Get all prices is not implemented yet"
    )


@router.get("/latest")
def get_latest_price(
    ticker: str = Query(..., description="Currency ticker, e.g. btc_usd")
):
    raise HTTPException(
        status_code=501,
        detail="Get latest price is not implemented yet"
    )


@router.get("/by-date")
def get_prices_by_date(
    ticker: str = Query(..., description="Currency ticker, e.g. btc_usd"),
    from_ts: int = Query(..., description="Start date (UNIX timestamp)"),
    to_ts: int = Query(..., description="End date (UNIX timestamp)")
):
    raise HTTPException(
        status_code=501,
        detail="Get prices by date is not implemented yet"
    )
