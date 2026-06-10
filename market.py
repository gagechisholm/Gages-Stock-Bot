import httpx
import asyncio
import os
import logging
import time
from dotenv import load_dotenv

load_dotenv()

MARKETSTACK_KEY = os.environ.get("MARKETSTACK_API_KEY", "")
BASE = "https://api.marketstack.com/v1"

# Simple in-memory cache: symbol -> (price_data, timestamp)
_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = 60  # seconds


def _cached(symbol: str) -> dict | None:
    entry = _cache.get(symbol.upper())
    if entry and (time.time() - entry[1]) < CACHE_TTL:
        return entry[0]
    return None


def _store(symbol: str, data: dict) -> None:
    _cache[symbol.upper()] = (data, time.time())


async def get_quote(symbol: str) -> dict | None:
    symbol = symbol.upper()
    cached = _cached(symbol)
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{BASE}/intraday/latest", params={
                "symbols": symbol,
                "access_key": MARKETSTACK_KEY,
            })
            r.raise_for_status()
            data = r.json().get("data", [])
            if not data:
                return None
            quote = data[0]
            _store(symbol, quote)
            return quote
    except httpx.HTTPStatusError as e:
        logging.warning(f"Marketstack HTTP error for {symbol}: {e.response.status_code}")
        return None
    except Exception:
        logging.exception(f"Unexpected error fetching quote for {symbol}")
        return None


async def get_quotes(symbols: list[str]) -> dict[str, dict]:
    """Fetch multiple quotes in one API call. Returns {symbol: quote_data}."""
    if not symbols:
        return {}

    upper = [s.upper() for s in symbols]

    # Return cached results without an API call if all are fresh
    results = {}
    missing = []
    for s in upper:
        cached = _cached(s)
        if cached:
            results[s] = cached
        else:
            missing.append(s)

    if not missing:
        return results

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(f"{BASE}/intraday/latest", params={
                "symbols": ",".join(missing),
                "access_key": MARKETSTACK_KEY,
            })
            r.raise_for_status()
            for item in r.json().get("data", []):
                sym = item["symbol"]
                _store(sym, item)
                results[sym] = item
    except Exception:
        logging.exception("Error fetching batch quotes from Marketstack")

    return results


async def validate_symbol(symbol: str) -> bool:
    quote = await get_quote(symbol)
    return quote is not None and quote.get("close") is not None


def format_quote(quote: dict) -> str:
    symbol = quote.get("symbol", "?")
    price = quote.get("close") or quote.get("last") or 0
    open_p = quote.get("open") or price
    change = price - open_p
    pct = (change / open_p * 100) if open_p else 0
    arrow = "▲" if change >= 0 else "▼"
    return (
        f"**{symbol}**  ${price:,.2f}  "
        f"{arrow} {abs(change):.2f} ({pct:+.2f}%)"
    )
