"""
ui/sidebar.py

Purpose
-------
The ONE place all run controls live: branding, market/date selection,
SMA10/EMA10 thresholds, and the Run Analysis button — all inside
st.sidebar. There is no separate "Settings" tab; this left-hand panel is
the single control surface, as requested.

Inputs
------
None (delegates the actual widgets to ui/controls.render_controls()).

Outputs
-------
dict — the same control-state dict ui/controls.render_controls() returns:
{
    "market": str, "option": str, "custom_date": date|None,
    "sma_threshold": float, "ema_threshold": float, "run_analysis": bool,
}

How it connects
----------------
app.py calls render_sidebar_controls() once, near the top of the script,
before anything else needs to know the user's selection (date label in
the header, the run loop, etc). The progress bar shown while a scan runs
is rendered separately by app.py, inside its own `with st.sidebar:`
block, so it appears right under the Run button.
"""

import streamlit as st

from config.settings import PAGE_TITLE
from ui.controls import render_controls
from ui.theme import render_html, COLORS


def render_sidebar_controls() -> dict:
    with st.sidebar:
        render_html(
            f"""
            <div class="mi-sidebar-brand">
                <div class="mi-sidebar-logo">📈</div>
                <div>
                    <div class="mi-sidebar-title">{PAGE_TITLE}</div>
                    <div class="mi-sidebar-sub">Trading Intelligence Panel</div>
                </div>
            </div>
            <style>
            .mi-sidebar-brand {{ display:flex; align-items:center; gap:10px; margin-bottom:18px; }}
            .mi-sidebar-logo {{
                width:36px; height:36px; border-radius:10px; display:flex; align-items:center;
                justify-content:center; font-size:1.1rem;
                background:linear-gradient(135deg, {COLORS['teal_soft']}, rgba(0,217,192,0.02));
                border:1px solid {COLORS['border_strong']};
            }}
            .mi-sidebar-title {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1rem; color:{COLORS['text']}; }}
            .mi-sidebar-sub {{ color:{COLORS['muted']}; font-size:0.72rem; }}
            </style>
            """,
        )

        state = render_controls()

    return state
