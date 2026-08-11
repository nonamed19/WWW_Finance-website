"""Market index API routes."""
from threading import Lock
from time import monotonic

import yfinance as yf
from fastapi import APIRouter, HTTPException


router = APIRouter(prefix="/markets", tags=["markets"])
_CACHE_TTL_SECONDS = 60
_cache: tuple[float, dict] | None = None
_cache_lock = Lock()


def _load_market_indices() -> dict:
    tickers = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Dow Jones": "^DJI",
        "Kospi": "^KS11",
    }
    history = yf.download(
        list(tickers.values()), period="5d", progress=False, threads=True
    )
    if history.empty or "Close" not in history:
        return {name: {"current_price": "N/A", "percentage_change": 0.0} for name in tickers}

    closes = history["Close"]
    data = {}
    for name, ticker in tickers.items():
        values = closes[ticker].dropna()
        if len(values) < 2:
            data[name] = {"current_price": "N/A", "percentage_change": 0.0}
            continue
        current, previous = float(values.iloc[-1]), float(values.iloc[-2])
        data[name] = {
            "current_price": round(current, 2),
            "percentage_change": round((current - previous) / previous * 100, 2),
        }
    return data


@router.get("/indices/")
def market_indices():
    global _cache
    now = monotonic()
    if _cache and now - _cache[0] < _CACHE_TTL_SECONDS:
        return _cache[1]
    try:
        with _cache_lock:
            # A second check prevents a burst of requests from downloading the
            # same four tickers while the first request is in flight.
            now = monotonic()
            if _cache and now - _cache[0] < _CACHE_TTL_SECONDS:
                return _cache[1]
            data = _load_market_indices()
            _cache = (now, data)
    except Exception as error:
        raise HTTPException(500, {"error": str(error)}) from error
    return data
