"""
ui/charts.py

Purpose
-------
Two kinds of visuals:
1. render_signal_distribution() — a real, working bar chart of how many
   stocks fall into each signal bucket (cheap, safe, already useful).
2. render_future_chart_gallery() — a grid of styled placeholders for the
   charts explicitly scoped as "future ready" in the brief (candlestick,
   SMA overlay, EMA overlay, RSI, Volume). No charting logic is
   implemented yet; swapping in a real plotting call later only touches
   ui/components.render_chart_placeholder, nothing else.

Inputs
------
counts: dict[str, int]  - signal label -> count, for the distribution chart
stock_name: str          - optional, used as the gallery's section title

Outputs
-------
None (renders directly).

How it connects
----------------
app.py calls render_signal_distribution() on the Dashboard tab, and
render_future_chart_gallery() can be dropped into any per-stock detail
view later (e.g. a future "Indian Market -> click a row" drill-down).
"""

import pandas as pd
import streamlit as st

from ui.components import render_section_header, render_chart_placeholder


def render_signal_distribution(counts: dict) -> None:
    if not counts or all(v == 0 for v in counts.values()):
        return

    render_section_header("📊", "Signal Distribution", "Stock count per signal bucket, this scan")

    df = pd.DataFrame({"Signal": list(counts.keys()), "Count": list(counts.values())})
    st.bar_chart(df.set_index("Signal"), color="#00D9C0")


def render_future_chart_gallery(stock_name: str = "Selected Stock") -> None:
    render_section_header("🕯️", "Chart Studio", f"Reserved layout for {stock_name} — wiring coming soon")

    cols = st.columns(2)
    specs = [
        ("Candlestick", "OHLC price action", "candlestick"),
        ("SMA Overlay", "SMA10 / SMA20 / SMA50 vs price", "sma"),
        ("EMA Overlay", "EMA10 trend line vs price", "ema"),
        ("RSI (14)", "Momentum oscillator, 30/70 bands", "rsi"),
        ("Volume", "Daily traded volume", "volume"),
    ]
    for i, (title, subtitle, kind) in enumerate(specs):
        with cols[i % 2]:
            render_chart_placeholder(title, subtitle, kind)
