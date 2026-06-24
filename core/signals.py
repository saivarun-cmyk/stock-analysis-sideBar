"""
core/signals.py

Purpose
-------
The decision logic: turns indicator values into the 5 +1/-1/0 conditions,
sums them into a score, and maps the score to a human-readable signal.
Ported 1:1 from the original app.py — same thresholds, same labels.

Inputs
------
compute_score(close, sma10, sma20, sma50, rsi, high20, low20) -> int
calculate_signal(score) -> str

Outputs
-------
An integer score in roughly [-5, 5], and one of:
"🔥 Strong Bullish", "✅ Bullish", "➖ Neutral", "⚠️ Bearish", "❌ Strong Bearish"

How it connects
----------------
core/analyzer.py calls compute_score() then calculate_signal() to finish
building the per-stock result dict. core/scanners.py reads the resulting
"Signal" field to bucket stocks for the Bullish/Neutral/Bearish tabs.
"""

from config.settings import (
    RSI_BULLISH,
    RSI_BEARISH,
    SCORE_STRONG_BULLISH,
    SCORE_BULLISH,
    SCORE_STRONG_BEARISH,
    SCORE_BEARISH,
)


def compute_score(close: float, sma10: float, sma20: float, sma50: float,
                   rsi: float, high20: float, low20: float) -> int:
    """Sum of the 5 original trend/momentum/breakout conditions."""
    cond1 = 1 if close > sma10 else -1
    cond2 = 1 if sma10 > sma20 else -1
    cond3 = 1 if sma20 > sma50 else -1

    if rsi > RSI_BULLISH:
        cond4 = 1
    elif rsi < RSI_BEARISH:
        cond4 = -1
    else:
        cond4 = 0

    if close >= high20:
        cond5 = 1
    elif close < low20:
        cond5 = -1
    else:
        cond5 = 0

    return cond1 + cond2 + cond3 + cond4 + cond5


def calculate_signal(score: int) -> str:
    """Map a numeric score to the original signal labels."""
    if score >= SCORE_STRONG_BULLISH:
        return "🔥 Strong Bullish"
    if score >= SCORE_BULLISH:
        return "✅ Bullish"
    if score <= SCORE_STRONG_BEARISH:
        return "❌ Strong Bearish"
    if score <= SCORE_BEARISH:
        return "⚠️ Bearish"
    return "➖ Neutral"
