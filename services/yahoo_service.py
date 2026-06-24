"""
services/yahoo_service.py

Purpose
-------
The single point of contact with yfinance. Owns the st.cache_data
decorator (cache duration driven by config/settings.CACHE_TIME), and
guarantees callers never see a raised exception — failures come back as
an empty DataFrame plus a logged error, exactly like the original app's
broad try/except.

Inputs
------
ticker: str   - a fully-qualified Yahoo Finance ticker (e.g. "TCS.NS", "AAPL", "^NSEI")
period: str   - yfinance period string, defaults to settings.YAHOO_PERIOD
interval: str - yfinance interval string, defaults to settings.YAHOO_INTERVAL

Outputs
-------
pandas.DataFrame with OHLCV columns (possibly empty on failure).

How it connects
----------------
Called exclusively by core/data_fetcher.py. No other module should import
yfinance directly — this keeps the network/caching concern in one place.
"""

import streamlit as st
import yfinance as yf
import pandas as pd

from config.settings import CACHE_TIME, YAHOO_PERIOD, YAHOO_INTERVAL
from utils.helpers import get_logger

logger = get_logger(__name__)


@st.cache_data(ttl=CACHE_TIME)
def fetch_ohlc(ticker: str, period: str = YAHOO_PERIOD, interval: str = YAHOO_INTERVAL) -> pd.DataFrame:
    """
    Download daily OHLC candles for a single ticker. Never raises —
    returns an empty DataFrame on any failure so callers can simply check
    `.empty`.
    """
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)

        if data is None or data.empty:
            logger.warning("No data returned for ticker=%s", ticker)
            return pd.DataFrame()

        return data

    except Exception as exc:  # noqa: BLE001 - intentional broad catch, mirrors original app
        logger.error("Failed to fetch ticker=%s: %s", ticker, exc)
        return pd.DataFrame()
