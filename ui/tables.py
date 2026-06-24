"""
ui/tables.py

Purpose
-------
Renders the trading-terminal-style results table: a search box, a sort
control, and a sticky-header glass table with a glowing badge for the
Signal column. Also provides the curated column view requested in the
design brief (Stock, Market, Date, Close Price, RSI, SMA10, EMA10,
Distance %, Score, Signal) while keeping the full result set available
for export.

Inputs
------
results: list[dict] | pd.DataFrame  - output of core/analyzer.py / core/scanners.py
title / subtitle: str               - section header text
key: str                            - unique Streamlit widget key prefix

Outputs
-------
pd.DataFrame - the full (unfiltered) DataFrame for this section, suitable
for passing straight into services/export_service.py.

How it connects
----------------
app.py calls render_results_section() once per tab (Indian Market, US
Market, Signals) with the list[dict] produced by core/analyzer.py and
core/scanners.py.
"""

import pandas as pd
import streamlit as st

from ui.components import render_section_header, render_searchable_table

DISPLAY_COLUMNS = ["Stock", "Market", "Date", "Close Price", "RSI", "SMA10", "EMA10", "Distance %", "Score", "Signal"]


def to_dataframe(results) -> pd.DataFrame:
    return results if isinstance(results, pd.DataFrame) else pd.DataFrame(results)


def to_display_view(df: pd.DataFrame) -> pd.DataFrame:
    """Curated, renamed column subset for on-screen display (export still uses the full df)."""
    if df.empty:
        return df
    view = df.rename(columns={"Close": "Close Price"})
    cols = [c for c in DISPLAY_COLUMNS if c in view.columns]
    return view[cols]


def render_results_section(icon: str, title: str, subtitle: str, results, key: str,
                            default_sort: str = "Score", default_ascending: bool = False) -> pd.DataFrame:
    df = to_dataframe(results)

    render_section_header(icon, title, subtitle)

    render_searchable_table(
        to_display_view(df),
        key=key,
        search_columns=["Stock", "Market"],
        badge_column="Signal",
        default_sort=default_sort,
        default_ascending=default_ascending,
    )

    return df


def render_download_button(column, label: str, df: pd.DataFrame, file_name: str, export_fn) -> None:
    """Render a download button only when there is data to export."""
    if df.empty:
        return
    with column:
        st.download_button(
            label=label,
            data=export_fn(df),
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
