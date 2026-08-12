"""
services/yahoo_service.py

Purpose
-------
The single point of contact with yfinance (and nselib for unsupported NSE indices). 
Owns the st.cache_data decorator (cache duration driven by config/settings.CACHE_TIME), 
and guarantees callers never see a raised exception — failures come back as
an empty DataFrame plus a logged error, exactly like the original app's
broad try/except.

Inputs
------
ticker: str   - a fully-qualified Yahoo Finance ticker (e.g. "TCS.NS", "AAPL", "^NSEI")
                OR an NSE pseudo-ticker (e.g., "NSE:NIFTY OIL AND GAS")
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
from datetime import datetime, timedelta

# Requires: pip install nselib
from nselib import capital_market 

from config.settings import CACHE_TIME, YAHOO_PERIOD, YAHOO_INTERVAL
from utils.helpers import get_logger

logger = get_logger(__name__)


def _get_nse_dates(period: str) -> tuple[str, str]:
    """Converts yfinance period strings into nselib DD-MM-YYYY date formats."""
    end_date = datetime.now()
    
    # Map common yfinance periods to days
    period_map = {
        '1mo': 30, '3mo': 90, '6mo': 180, 
        '1y': 365, '2y': 730, '5y': 1825
    }
    days = period_map.get(period, 180) # Default to 6 months
    
    start_date = end_date - timedelta(days=days)
    
    return start_date.strftime("%d-%m-%Y"), end_date.strftime("%d-%m-%Y")


def _fetch_from_nse(index_name: str, period: str) -> pd.DataFrame:
    """Fallback fetcher using nselib for unsupported NSE thematic indices."""
    try:
        from_date, to_date = _get_nse_dates(period)

        # Work around a bug in nselib.capital_market.get_index_data(): it does
        # index.replace(" ", "%20") but never encodes "&", so any index whose
        # real NSE name contains "&" (e.g. "Nifty EV & New Age Automotive")
        # breaks the query string -- the "&" is read as a new query param
        # delimiter and NSE silently returns nothing for the truncated name.
        # nselib has a cleaning_nse_symbol() helper elsewhere that does this
        # exact "&" -> "%26" substitution for stock symbols like "M&M", but
        # it's never applied inside get_index_data(). Pre-encoding it here is
        # safe either way: get_index_data()'s own .replace(" ", "%20").upper()
        # leaves an existing "%26" untouched.
        safe_index_name = index_name.replace("&", "%26")

        # Fetch directly from NSE
        df = capital_market.index_data(index=safe_index_name, from_date=from_date, to_date=to_date)
        
        if df is None or df.empty:
            logger.warning("NSE fetch returned no rows for index=%s (encoded=%s)", index_name, safe_index_name)
            return pd.DataFrame()
            
        # Clean and format to perfectly match yfinance's structure.
        # NOTE: nselib's capital_market.index_data() actually returns columns
        # ['INDEX_NAME', 'OPEN_INDEX_VAL', 'HIGH_INDEX_VAL', 'CLOSE_INDEX_VAL',
        #  'LOW_INDEX_VAL', 'TURN_OVER', 'TRADED_QTY', 'TIMESTAMP'] -- there is
        # no 'HistoricalDate'/'OPEN'/'HIGH'/'LOW'/'CLOSE'. Using the wrong
        # names silently raised a KeyError that was swallowed by the except
        # block below, so every NSE: index came back empty. dayfirst=True
        # since NSE's TIMESTAMP is "DD-Mon-YYYY".
        df['Date'] = pd.to_datetime(df['TIMESTAMP'], dayfirst=True, errors='coerce')

        # CRITICAL: any row whose TIMESTAMP failed to parse becomes NaT, and
        # pandas sorts NaT to the END of an ascending sort_index() -- which is
        # exactly what core/data_fetcher.get_prepared_data() calls right after
        # this, and select_row()'s "Today" is literally data.iloc[-1]. A single
        # bad TIMESTAMP therefore silently replaces "today's" real row with
        # garbage, corrupting every indicator/score downstream. Drop it here.
        bad_rows = df['Date'].isna().sum()
        if bad_rows:
            logger.warning(
                "Dropping %d row(s) with unparseable TIMESTAMP for index=%s (sample: %s)",
                bad_rows, index_name, df.loc[df['Date'].isna(), 'TIMESTAMP'].head(3).tolist(),
            )
            df = df.dropna(subset=['Date'])

        if df.empty:
            return pd.DataFrame()

        df.set_index('Date', inplace=True)
        
        # Strip commas from numbers and convert to float
        for col in ['OPEN_INDEX_VAL', 'HIGH_INDEX_VAL', 'LOW_INDEX_VAL', 'CLOSE_INDEX_VAL']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').astype(float)
                
        df.rename(columns={
            'OPEN_INDEX_VAL': 'Open',
            'HIGH_INDEX_VAL': 'High',
            'LOW_INDEX_VAL': 'Low',
            'CLOSE_INDEX_VAL': 'Close',
        }, inplace=True)
        
        # nselib indices lack volume data, pad with 0s to prevent KeyError in UI charts
        df['Volume'] = 0 
        
        # Sort chronologically (nselib sometimes returns newest first)
        df = df.sort_index()
        
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
    except Exception as exc:
        logger.error("NSE fetch failed for index=%s: %s: %s", index_name, type(exc).__name__, exc, exc_info=True)
        return pd.DataFrame()


@st.cache_data(ttl=CACHE_TIME)
def fetch_ohlc(ticker: str, period: str = YAHOO_PERIOD, interval: str = YAHOO_INTERVAL) -> pd.DataFrame:
    """
    Download daily OHLC candles for a single ticker. Never raises —
    returns an empty DataFrame on any failure so callers can simply check
    `.empty`. Routes "NSE:..." tickers to nselib directly.
    """
    try:
        # Route specific thematic indices to nselib
        if ticker.startswith("NSE:"):
            nse_index = ticker.replace("NSE:", "")
            data = _fetch_from_nse(nse_index, period)
            
        # Default routing to yfinance
        else:
            data = yf.download(ticker, period=period, interval=interval, progress=False)

        if data is None or data.empty:
            logger.warning("No data returned for ticker=%s", ticker)
            return pd.DataFrame()

        return data

    except Exception as exc:  # noqa: BLE001 - intentional broad catch, mirrors original app
        logger.error("Failed to fetch ticker=%s: %s", ticker, exc)
        return pd.DataFrame()
