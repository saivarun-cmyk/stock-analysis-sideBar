"""
config/settings.py

Purpose
-------
Single source of truth for every "magic number" in the app. Nothing else in
the codebase should hard-code a cache TTL, a default threshold, or a
yfinance period/interval — they all read from here.

Inputs
------
None (static constants).

Outputs
-------
Module-level constants imported by other layers.

How it connects
----------------
- services/yahoo_service.py reads CACHE_TIME, YAHOO_PERIOD, YAHOO_INTERVAL.
- core/data_fetcher.py reads MIN_DATA_POINTS.
- core/indicators.py reads SMA_WINDOWS, EMA_SPAN, RSI_PERIOD, BREAKOUT_WINDOW.
- ui/sidebar.py reads DEFAULT_SMA_THRESHOLD, DEFAULT_EMA_THRESHOLD,
  SMA_THRESHOLD_RANGE for the slider bounds.
- app.py reads TIMEZONES, PAGE_TITLE, PAGE_ICON.

NOTE: the original app.py used st.cache_data(ttl=900). This file follows
the user's explicitly requested defaults (CACHE_TIME=300 etc). Change the
value below if you want to restore the original 15-minute cache.
"""

# ----------------------------------------------------------------------
# Caching
# ----------------------------------------------------------------------
CACHE_TIME = 300  # seconds. Original app.py used 900 — change here if needed.

# ----------------------------------------------------------------------
# Scanner thresholds (defaults shown on the sidebar sliders)
# ----------------------------------------------------------------------
DEFAULT_SMA_THRESHOLD = 2
DEFAULT_EMA_THRESHOLD = 2
SMA_THRESHOLD_RANGE = (0.5, 5.0, 0.5)  # (min, max, step) — matches original slider
EMA_THRESHOLD_RANGE = (0.5, 5.0, 0.5)

# ----------------------------------------------------------------------
# Yahoo Finance fetch parameters
# ----------------------------------------------------------------------
YAHOO_PERIOD = "6mo"
YAHOO_INTERVAL = "1d"
MIN_DATA_POINTS = 50  # rows required before indicators are considered valid

# ----------------------------------------------------------------------
# Indicator parameters
# ----------------------------------------------------------------------
SMA_WINDOWS = {"SMA10": 10, "SMA20": 20, "SMA50": 50}
EMA_SPAN = 10
RSI_PERIOD = 14
BREAKOUT_WINDOW = 20  # 20-day high/low lookback

# ----------------------------------------------------------------------
# Scoring thresholds (used by core/signals.py)
# ----------------------------------------------------------------------
RSI_BULLISH = 55
RSI_BEARISH = 45
SCORE_STRONG_BULLISH = 4
SCORE_BULLISH = 2
SCORE_STRONG_BEARISH = -4
SCORE_BEARISH = -2

# ----------------------------------------------------------------------
# UI / page
# ----------------------------------------------------------------------
PAGE_TITLE = "Stock Analysis Suite V2"
PAGE_ICON = "📈"
TIMEZONES = {
    "India": "Asia/Kolkata",
    "USA": "America/New_York",
}

# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
