"""
utils/helpers.py

Purpose
-------
Small, pure, framework-agnostic helpers used across layers: logging setup
and safe numeric conversion. Nothing here imports streamlit, yfinance, or
pandas business logic — keep it that way so it stays trivially testable.

Inputs / Outputs
-----------------
get_logger(name) -> logging.Logger
safe_float(value) -> float | None
any_nan(values: list) -> bool

How it connects
----------------
Every layer (services, core, ui, app.py) calls get_logger(__name__) for
consistent log formatting. core/data_fetcher.py and core/analyzer.py use
safe_float/any_nan to replicate the original app's NaN-guard behavior.
"""

import logging

from config.settings import LOG_LEVEL, LOG_FORMAT

_CONFIGURED = False


def _configure_root_logger() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    logging.basicConfig(level=getattr(logging, LOG_LEVEL, "INFO"), format=LOG_FORMAT)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger with consistent formatting/level."""
    _configure_root_logger()
    return logging.getLogger(name)


def safe_float(value) -> float | None:
    """Convert a value to float, returning None instead of raising."""
    try:
        result = float(value)
        return None if result != result else result  # filters NaN (NaN != NaN)
    except (TypeError, ValueError):
        return None


def any_nan(values: list) -> bool:
    """True if any element in values is None or NaN."""
    return any(v is None for v in (safe_float(v) for v in values))


def is_market_open(now_local, open_time=(9, 15), close_time=(15, 30)) -> bool:
    """
    Pure helper for UI market-status pills: True if `now_local` (a
    timezone-aware datetime already converted to the relevant exchange's
    local time) falls within regular trading hours on a weekday.
    Defaults match NSE (India) hours; pass different open/close tuples
    for other exchanges (e.g. US: (9, 30) to (16, 0)).
    """
    if now_local.weekday() >= 5:  # Saturday/Sunday
        return False
    open_h, open_m = open_time
    close_h, close_m = close_time
    minutes_now = now_local.hour * 60 + now_local.minute
    return (open_h * 60 + open_m) <= minutes_now <= (close_h * 60 + close_m)


def expected_calendar_date(option: str, custom_date=None):
    """
    The calendar date the user *nominally* asked for, given their date
    option. This is intentionally NOT what gets analyzed (analysis always
    uses the latest available trading candle, per core/data_fetcher.py) —
    it exists only so the UI can detect "the candle I got doesn't match
    the calendar date you picked" and explain why (different exchange,
    market holiday, etc.) instead of silently showing a mismatched date.
    """
    from datetime import date, timedelta

    if option == "Today":
        return date.today()
    if option == "Yesterday":
        return date.today() - timedelta(days=1)
    if option == "Custom Date":
        return custom_date
    return None


def most_common_result_date(results: list) -> str | None:
    """The most frequent 'Date' value across a list of analyzer result dicts."""
    from collections import Counter

    dates = [r["Date"] for r in results if r.get("Date")]
    if not dates:
        return None
    return Counter(dates).most_common(1)[0][0]


def build_date_fallback_note(option: str, custom_date, results: list, market_label: str) -> str | None:
    """
    Compares the nominal requested date against the actual candle date
    that came back from Yahoo Finance for a market's results. Returns a
    human-readable note when they differ (e.g. US market still trading
    the prior session while it's already "today" in India), or None when
    they match.
    """
    expected = expected_calendar_date(option, custom_date)
    if expected is None or not results:
        return None

    actual = most_common_result_date(results)
    if actual is None or actual == str(expected):
        return None

    return (
        f"{market_label}: {expected.strftime('%d-%b-%Y')} not available (market closed or "
        f"not yet settled). Showing latest available trading session — {actual}."
    )
