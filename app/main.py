from fastapi import FastAPI

from app.api.routes import router as prices_router

app = FastAPI(title="Deribit Price Tracker")

app.include_router(prices_router)


@app.get("/health")
def health():
    return {"status": "ok"}
