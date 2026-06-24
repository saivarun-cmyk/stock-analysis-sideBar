"""
core/indicators.py

Purpose
-------
All technical-indicator math, ported 1:1 from the original app.py. Pure
pandas in, pandas out — no Streamlit, no network calls, no business
decisions (signal logic lives in core/signals.py).

Inputs
------
A DataFrame with at least "High", "Low", "Close" columns (as returned by
yfinance / core/data_fetcher.py).

Outputs
-------
Either an individual pandas Series (calculate_sma/calculate_ema/calculate_rsi)
or a tuple of Series (calculate_high_low), plus a convenience
add_all_indicators(df) that mutates a copy of df with every indicator column
the original app.py computed — same column names, same math, same order.

How it connects
----------------
core/data_fetcher.py calls add_all_indicators() right after cleaning the
raw OHLC data. core/analyzer.py then reads the indicator columns off the
returned DataFrame.
"""

import pandas as pd

from config.settings import SMA_WINDOWS, EMA_SPAN, RSI_PERIOD, BREAKOUT_WINDOW


def calculate_sma(df: pd.DataFrame, window: int, column: str = "Close") -> pd.Series:
    """Simple moving average over `window` periods."""
    return df[column].rolling(window).mean()


def calculate_ema(df: pd.DataFrame, span: int, column: str = "Close") -> pd.Series:
    """Exponential moving average with the same ewm params as the original app."""
    return df[column].ewm(span=span, adjust=False).mean()


def calculate_rsi(df: pd.DataFrame, period: int = RSI_PERIOD, column: str = "Close") -> pd.Series:
    """
    Wilder-style RSI, identical formula to the original app:
    ewm(alpha=1/period, min_periods=period, adjust=False) on gains/losses.
    """
    delta = df[column].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_high_low(df: pd.DataFrame, window: int = BREAKOUT_WINDOW) -> tuple[pd.Series, pd.Series]:
    """
    Rolling N-day high/low, shifted by 1 so "today" is compared against the
    prior N days only (matches the original breakout logic exactly).
    """
    high = df["High"].rolling(window).max().shift(1)
    low = df["Low"].rolling(window).min().shift(1)
    return high, low


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience wrapper: returns a copy of df with every indicator column
    the original app computed, using the exact same column names so the
    rest of the pipeline (analyzer/signals) is a direct port.
    """
    data = df.copy()

    data["SMA10"] = calculate_sma(data, SMA_WINDOWS["SMA10"])
    data["SMA20"] = calculate_sma(data, SMA_WINDOWS["SMA20"])
    data["SMA50"] = calculate_sma(data, SMA_WINDOWS["SMA50"])

    data["EMA10"] = calculate_ema(data, EMA_SPAN)

    data["RSI"] = calculate_rsi(data)

    data["20D_High"], data["20D_Low"] = calculate_high_low(data)

    return data
