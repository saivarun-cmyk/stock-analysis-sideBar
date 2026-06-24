"""
ui/controls.py

Purpose
-------
The full control form (market, date option, thresholds, run button).
Rendered inline wherever the caller's `with` context points — exclusively
inside the left sidebar (ui/sidebar.py), which is the single control
surface for the app. Mirrors its state into st.session_state["mi_controls"]
so other components (the header's "Selected: Today" chip) can read the
current selection.

Inputs
------
None (reads defaults from config/settings.py).

Outputs
-------
dict (also mirrored into st.session_state["mi_controls"]):
{
    "market": "All" | "India" | "USA",
    "option": "Today" | "Yesterday" | "Custom Date",
    "custom_date": date | None,
    "sma_threshold": float,
    "ema_threshold": float,
    "run_analysis": bool,
}

How it connects
----------------
ui/sidebar.render_sidebar_controls() calls this inside `with st.sidebar:`.
"""

import streamlit as st

from config.settings import (
    DEFAULT_SMA_THRESHOLD,
    DEFAULT_EMA_THRESHOLD,
    SMA_THRESHOLD_RANGE,
    EMA_THRESHOLD_RANGE,
)
from ui.components import render_section_header


def render_controls() -> dict:
    render_section_header("⚙️", "Scanner Settings", "Configure the universe, date, and scanner thresholds")

    st.markdown("**Market**")
    market = st.radio(
        "Market", ["All", "India", "USA"], index=0,
        label_visibility="collapsed", key="ctrl_market",
    )

    st.markdown("**Date**")
    option = st.radio(
        "Select Date Option", ["Today", "Yesterday", "Custom Date"],
        label_visibility="collapsed", key="ctrl_option",
    )

    custom_date = None
    if option == "Custom Date":
        custom_date = st.date_input("Choose Date", format="DD/MM/YYYY", key="ctrl_custom_date")

    st.markdown("---")

    sma_min, sma_max, sma_step = SMA_THRESHOLD_RANGE
    sma_threshold = st.slider(
        "🎯 SMA10 Distance %", min_value=sma_min, max_value=sma_max,
        value=float(DEFAULT_SMA_THRESHOLD), step=sma_step, key="ctrl_sma",
    )

    ema_min, ema_max, ema_step = EMA_THRESHOLD_RANGE
    ema_threshold = st.slider(
        "📈 EMA10 Distance %", min_value=ema_min, max_value=ema_max,
        value=float(DEFAULT_EMA_THRESHOLD), step=ema_step, key="ctrl_ema",
    )

    st.markdown("")
    run_analysis = st.button("🚀 Run Analysis", use_container_width=True, key="ctrl_run")

    state = {
        "market": market,
        "option": option,
        "custom_date": custom_date,
        "sma_threshold": sma_threshold,
        "ema_threshold": ema_threshold,
        "run_analysis": run_analysis,
    }
    st.session_state["mi_controls"] = state
    return state
