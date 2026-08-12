"""
core/data_fetcher.py

Purpose
-------
Bridges config (stock symbols) and services/yahoo_service (raw download)
into a clean, indicator-enriched DataFrame, then picks the single row the
rest of the pipeline cares about (Today / Yesterday / Custom Date) —
exactly the same selection logic as the original app.py.

Inputs
------
symbol: str          - ticker as stored in config/stocks_config.py
market: str           - "INDIA" or "USA"
option: str           - "Today" | "Yesterday" | "Custom Date"
custom_date: date|None - required when option == "Custom Date"

Outputs
-------
get_prepared_data(symbol, market) -> pd.DataFrame (cleaned, indicator columns added, or empty)
select_row(data, option, custom_date) -> pd.Series | None

How it connects
----------------
core/analyzer.py calls get_prepared_data() then select_row() to obtain the
single row of values it needs to build the result dict.
"""

import pandas as pd

from config.settings import MIN_DATA_POINTS
from core.indicators import add_all_indicators
from services.yahoo_service import fetch_ohlc
from utils.helpers import get_logger

logger = get_logger(__name__)


def build_ticker(symbol: str, market: str) -> str:
    """
    Normalize a config symbol into a valid Yahoo Finance ticker.
    Idempotent: if the symbol already has the right suffix/prefix
    (as config/stocks_config.py now provides), it is returned unchanged.
    Mirrors the original app's suffixing rule for INDIA market.
    """
    if market == "INDIA":
        if symbol.startswith("^") or symbol.startswith("NSE:") or symbol.endswith(".NS"):
            return symbol
        return f"{symbol}.NS"
    return symbol


def get_prepared_data(symbol: str, market: str) -> pd.DataFrame:
    """
    Fetch, flatten, clean, and enrich OHLC data for one ticker.
    Returns an empty DataFrame if data is unavailable or insufficient
    (same MIN_DATA_POINTS guard as the original app).
    """
    ticker = build_ticker(symbol, market)
    data = fetch_ohlc(ticker)

    if data.empty:
        return pd.DataFrame()

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Defensive data-handling (no calculation changes): guarantee chronological
    # order and drop fully-empty rows before anything downstream reads "the
    # latest row" as today's candle. yfinance normally returns sorted data,
    # but sorting explicitly removes any ambiguity about which row is latest.
    data = data.sort_index()
    data = data.dropna(how="all")

    if "Close" not in data.columns:
        logger.warning("No Close column for ticker=%s", ticker)
        return pd.DataFrame()

    data = data.dropna(subset=["Close"])

    if len(data) < MIN_DATA_POINTS:
        return pd.DataFrame()

    return add_all_indicators(data)


def select_row(data: pd.DataFrame, option: str, custom_date) -> pd.Series | None:
    """
    Pick the row matching the user's date selection, identical semantics
    to the original app.py:
      - Today: last row
      - Yesterday: second-to-last row (None if fewer than 2 rows)
      - Custom Date: last row on/before the chosen date

    Note on USA date handling: "Today" always resolves to the LAST row of
    `data` (the most recent candle Yahoo Finance has actually published),
    never to today's calendar date. This is intentional and correct —
    India and the US close on different trading calendars/timezones, so
    "today" in IST can still be mid-session (or not yet started) in New
    York. The caller (core/analyzer.py) reports the row's own index date
    as the result's "Date" field, so the UI always shows the real candle
    date rather than assuming it equals today's calendar date.
    """
    if option == "Today":
        return data.iloc[-1]

    if option == "Yesterday":
        if len(data) < 2:
            return None
        return data.iloc[-2]

    if option == "Custom Date":
        dated = data.copy()
        dated["Date"] = dated.index.date
        filtered = dated[dated["Date"] <= custom_date]
        if filtered.empty:
            return None
        return filtered.iloc[-1]

    return None
