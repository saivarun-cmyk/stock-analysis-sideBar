"""
core/analyzer.py

Purpose
-------
The single entry point for "analyze one stock". Glues together
data_fetcher (network+cleaning), indicators (already embedded in the
fetched DataFrame), and signals (scoring) into the exact result dict
shape the original app.py produced — so every downstream consumer
(scanners, tables, export) needs zero changes.

Inputs
------
stock_name: str   - display name, e.g. "TCS"
symbol: str        - ticker as stored in config/stocks_config.py
market: str        - "INDIA" or "USA"
option: str        - "Today" | "Yesterday" | "Custom Date"
custom_date: date|None

Outputs
-------
dict | None  - None if data was unavailable/insufficient/NaN, otherwise:
{
    "Stock": str, "Market": str, "Date": str,
    "Close": float, "SMA10": float, "SMA20": float, "SMA50": float,
    "EMA10": float, "EMA Distance %": float, "RSI": float,
    "Distance %": float, "Side": str, "Score": int, "Signal": str,
    "Sector": str,
}

How it connects
----------------
app.py calls analyze_stock() once per stock in config/stocks_config.py
inside the main run loop. core/scanners.py consumes the list of dicts
this function produces.
"""

from core.data_fetcher import get_prepared_data, select_row
from core.signals import compute_score, calculate_signal
from utils.helpers import safe_float, any_nan, get_logger

logger = get_logger(__name__)


def analyze_stock(stock_name: str, symbol: str, market: str, option: str,
                   custom_date, sector: str = "N/A") -> dict | None:
    """Run the full analysis pipeline for a single stock. Never raises."""
    try:
        data = get_prepared_data(symbol, market)
        if data.empty:
            return None

        latest = select_row(data, option, custom_date)
        if latest is None:
            return None

        close_price = safe_float(latest["Close"])
        sma10 = safe_float(latest["SMA10"])
        sma20 = safe_float(latest["SMA20"])
        sma50 = safe_float(latest["SMA50"])
        ema10 = safe_float(latest["EMA10"])
        rsi = safe_float(latest["RSI"])
        high20 = safe_float(latest["20D_High"])
        low20 = safe_float(latest["20D_Low"])

        if any_nan([close_price, sma10, sma20, sma50, rsi, high20, low20]):
            return None

        score = compute_score(close_price, sma10, sma20, sma50, rsi, high20, low20)
        signal = calculate_signal(score)

        distance = (abs(close_price - sma10) / sma10) * 100
        ema_distance = (abs(close_price - ema10) / ema10) * 100
        side = "Above SMA10" if close_price > sma10 else "Below SMA10"

        return {
            "Stock": stock_name,
            "Market": market,
            "Sector": sector,
            "Date": str(latest.name.date()),
            "Close": round(close_price, 2),
            "SMA10": round(sma10, 2),
            "SMA20": round(sma20, 2),
            "SMA50": round(sma50, 2),
            "EMA10": round(ema10, 2),
            "EMA Distance %": round(ema_distance, 2),
            "RSI": round(rsi, 2),
            "Distance %": round(distance, 2),
            "Side": side,
            "Score": score,
            "Signal": signal,
        }

    except Exception as exc:  # noqa: BLE001 - mirrors original app's broad guard
        logger.error("analyze_stock failed for %s (%s): %s", stock_name, symbol, exc)
        return None
