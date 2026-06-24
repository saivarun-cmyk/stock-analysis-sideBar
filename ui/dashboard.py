"""
ui/dashboard.py

Purpose
-------
Renders the 7 KPI cards (Total Analysed, Strong Bullish, Bullish, Neutral,
Bearish, SMA10 Opportunities, EMA10 Opportunities) as an animated glass
grid, and computes the "+N vs previous scan" trend by comparing against
the last run's counts stored in st.session_state. Pure presentation —
takes pre-computed counts in.

Inputs
------
counts: dict with keys "total", "strong_bullish", "bullish", "neutral",
        "bearish", "sma10", "ema10"

Outputs
-------
None (renders the KPI grid). Also updates
st.session_state["mi_prev_counts"] so the *next* run can show a delta.

How it connects
----------------
app.py calls render_kpis(counts) once per completed analysis run, after
core/scanners.py has produced the bucketed results.
"""

import streamlit as st

from ui.components import render_kpi_grid


def render_kpis(counts: dict) -> None:
    previous = st.session_state.get("mi_prev_counts")

    def delta(key: str):
        if not previous:
            return None
        return counts.get(key, 0) - previous.get(key, 0)

    total = counts.get("total", 0)

    cards = [
        {
            "icon": "📊", "label": "Total Analysed", "value": total,
            "sub": "stocks scanned this run", "delta": delta("total"), "accent": "teal",
        },
        {
            "icon": "🔥", "label": "Strong Bullish", "value": counts.get("strong_bullish", 0),
            "sub": f"of {total} stocks", "delta": delta("strong_bullish"), "accent": "green",
        },
        {
            "icon": "✅", "label": "Bullish", "value": counts.get("bullish", 0),
            "sub": f"of {total} stocks", "delta": delta("bullish"), "accent": "green",
        },
        {
            "icon": "➖", "label": "Neutral", "value": counts.get("neutral", 0),
            "sub": f"of {total} stocks", "delta": delta("neutral"), "accent": "amber",
        },
        {
            "icon": "⚠️", "label": "Bearish", "value": counts.get("bearish", 0),
            "sub": f"of {total} stocks", "delta": delta("bearish"), "accent": "orange",
        },
        {
            "icon": "🎯", "label": "SMA10 Opportunities", "value": counts.get("sma10", 0),
            "sub": "near SMA10 support/resistance", "delta": delta("sma10"), "accent": "teal",
        },
        {
            "icon": "📈", "label": "EMA10 Opportunities", "value": counts.get("ema10", 0),
            "sub": "near EMA10 threshold", "delta": delta("ema10"), "accent": "teal",
        },
    ]

    render_kpi_grid(cards)

    st.session_state["mi_prev_counts"] = counts
