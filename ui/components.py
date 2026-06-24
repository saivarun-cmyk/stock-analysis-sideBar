"""
ui/components.py

Purpose
-------
Reusable presentation building blocks used across every page. These
render plain HTML/CSS via st.markdown(unsafe_allow_html=True) — they take
already-computed data in (counts, dicts, DataFrames) and never perform
calculations themselves.

Inputs / Outputs
-----------------
render_kpi_grid(cards: list[dict]) -> None
render_market_status(india_open: bool, usa_open: bool, last_updated: str) -> None
signal_badge_html(signal: str) -> str
render_searchable_table(df, key, search_columns, badge_column) -> pd.DataFrame (filtered/sorted view actually shown)
render_chart_placeholder(title, subtitle, kind) -> None
render_section_header(icon, title, subtitle) -> None
render_opportunity_card(...) -> None   # used by the SMA/EMA scanner pages

How it connects
----------------
ui/dashboard.py, ui/tables.py, ui/charts.py, and app.py all import from
here so every page shares one visual vocabulary instead of re-implementing
HTML snippets.
"""

import html as _html

import pandas as pd
import streamlit as st

from ui.theme import COLORS, SIGNAL_STYLE, render_html


# ======================================================================
# KPI CARDS
# ======================================================================

def render_kpi_grid(cards: list[dict]) -> None:
    """
    cards: list of {
        "icon": "🔥", "label": "Strong Bullish", "value": 12,
        "sub": "of 63 scanned", "delta": 5, "accent": "green"
    }
    accent must be one of: teal, green, red, amber, orange
    """
    items_html = []
    for c in cards:
        accent = COLORS.get(c.get("accent", "teal"), COLORS["teal"])
        delta = c.get("delta")
        if delta is None or delta == 0:
            delta_html = f'<span class="mi-kpi-delta mi-flat">— vs last scan</span>'
        elif delta > 0:
            delta_html = f'<span class="mi-kpi-delta mi-up">▲ +{delta} vs last scan</span>'
        else:
            delta_html = f'<span class="mi-kpi-delta mi-down">▼ {delta} vs last scan</span>'

        items_html.append(f"""
        <div class="mi-kpi-card mi-fade-in" style="--accent:{accent}">
            <div class="mi-kpi-top">
                <span class="mi-kpi-icon">{c['icon']}</span>
                <span class="mi-kpi-label">{_html.escape(str(c['label']))}</span>
            </div>
            <div class="mi-kpi-value">{c['value']}</div>
            <div class="mi-kpi-sub">{_html.escape(str(c.get('sub', '')))}</div>
            {delta_html}
        </div>
        """)

    render_html(
        f"""
        <style>
        .mi-kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 6px 0 18px 0;
        }}
        .mi-kpi-card {{
            position: relative;
            background: linear-gradient(180deg, {COLORS['panel']}, {COLORS['panel_alt']});
            border: 1px solid {COLORS['border']};
            border-radius: 14px;
            padding: 14px 14px 12px 14px;
            overflow: hidden;
            transition: transform 0.15s ease, border-color 0.15s ease;
        }}
        .mi-kpi-card::before {{
            content: "";
            position: absolute; top: 0; left: 0; right: 0; height: 3px;
            background: var(--accent);
            opacity: 0.9;
        }}
        .mi-kpi-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent);
        }}
        .mi-kpi-top {{ display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }}
        .mi-kpi-icon {{ font-size: 1.05rem; }}
        .mi-kpi-label {{
            font-size: 0.74rem; font-weight: 600; text-transform: uppercase;
            letter-spacing: 0.04em; color: {COLORS['muted']};
        }}
        .mi-kpi-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.65rem; font-weight: 600; color: {COLORS['text']};
            line-height: 1.1;
        }}
        .mi-kpi-sub {{ font-size: 0.72rem; color: {COLORS['faint']}; margin-top: 3px; }}
        .mi-kpi-delta {{
            display: inline-block; margin-top: 8px; font-size: 0.72rem;
            font-family: 'JetBrains Mono', monospace; font-weight: 500;
        }}
        .mi-up {{ color: {COLORS['green']}; }}
        .mi-down {{ color: {COLORS['red']}; }}
        .mi-flat {{ color: {COLORS['faint']}; }}
        @media (max-width: 640px) {{
            .mi-kpi-grid {{ grid-template-columns: repeat(2, 1fr); gap: 8px; }}
            .mi-kpi-value {{ font-size: 1.35rem; }}
        }}
        </style>
        <div class="mi-kpi-grid">{''.join(items_html)}</div>
        """,
    )


# ======================================================================
# MARKET STATUS HEADER
# ======================================================================

def render_market_status(india_open: bool, usa_open: bool, ist_time: str, usa_time: str,
                          last_updated: str, selected_date_label: str = "Today") -> None:
    def pill(label: str, is_open: bool) -> str:
        color = COLORS["green"] if is_open else COLORS["faint"]
        state = "OPEN" if is_open else "CLOSED"
        return f"""
        <div class="mi-status-pill">
            <span class="mi-pulse-dot" style="background:{color}; {'animation:none;' if not is_open else ''}"></span>
            <span class="mi-status-label">{label}</span>
            <span class="mi-status-state" style="color:{color}">{state}</span>
        </div>
        """

    render_html(
        f"""
        <style>
        .mi-header {{
            background: linear-gradient(135deg, {COLORS['panel']}, {COLORS['panel_alt']});
            border: 1px solid {COLORS['border']};
            border-radius: 16px;
            padding: 18px 20px;
            margin-bottom: 16px;
        }}
        .mi-header-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.5rem; font-weight: 700; color: {COLORS['text']};
            margin: 0 0 2px 0;
        }}
        .mi-header-sub {{ color: {COLORS['muted']}; font-size: 0.85rem; margin-bottom: 14px; }}
        .mi-status-row {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }}
        .mi-status-pill {{
            display: flex; align-items: center; gap: 6px;
            background: {COLORS['panel_alt']}; border: 1px solid {COLORS['border_strong']};
            border-radius: 999px; padding: 6px 12px; font-size: 0.78rem;
        }}
        .mi-status-label {{ color: {COLORS['muted']}; }}
        .mi-status-state {{ font-family: 'JetBrains Mono', monospace; font-weight: 600; }}
        .mi-time-chip {{
            font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: {COLORS['muted']};
            background: {COLORS['panel_alt']}; border: 1px solid {COLORS['border']};
            border-radius: 999px; padding: 6px 12px;
        }}
        @media (max-width: 640px) {{
            .mi-header {{ padding: 14px 14px; }}
            .mi-header-title {{ font-size: 1.15rem; }}
            .mi-status-row {{ gap: 8px; }}
        }}
        </style>
        <div class="mi-header mi-fade-in">
            <div class="mi-header-title">📈 Market Intelligence Dashboard</div>
            <div class="mi-header-sub">India + USA Stocks · SMA10/EMA10 Scanner · Bullish / Neutral / Bearish</div>
            <div class="mi-status-row">
                {pill("Indian Market", india_open)}
                {pill("US Market", usa_open)}
                <span class="mi-time-chip">🇮🇳 IST {ist_time}</span>
                <span class="mi-time-chip">🇺🇸 EST {usa_time}</span>
                <span class="mi-time-chip">⟳ Updated {last_updated}</span>
                <span class="mi-time-chip">📅 Selected: {selected_date_label}</span>
            </div>
        </div>
        """,
    )


# ======================================================================
# SIGNAL BADGE
# ======================================================================

def signal_badge_html(signal: str) -> str:
    color, bg, glow = SIGNAL_STYLE.get(signal, (COLORS["muted"], COLORS["panel_alt"], False))
    glow_css = f"box-shadow: 0 0 10px 0 {color}55;" if glow else ""
    label = _html.escape(signal)
    return (
        f'<span class="mi-badge" style="color:{color}; background:{bg}; '
        f'border:1px solid {color}55; {glow_css}">{label}</span>'
    )


# ======================================================================
# SECTION HEADER
# ======================================================================

def render_section_header(icon: str, title: str, subtitle: str = "") -> None:
    render_html(
        f"""
        <div class="mi-fade-in" style="margin: 6px 0 14px 0;">
            <div style="font-family:'Space Grotesk',sans-serif; font-size:1.15rem; font-weight:700;
                        color:{COLORS['text']};">{icon} {_html.escape(title)}</div>
            {f'<div style="color:{COLORS["muted"]}; font-size:0.82rem; margin-top:2px;">{_html.escape(subtitle)}</div>' if subtitle else ''}
        </div>
        """,
    )


# ======================================================================
# SEARCHABLE / SORTABLE STYLED TABLE (with badge column support)
# ======================================================================

def render_searchable_table(df: pd.DataFrame, key: str, search_columns: list[str] | None = None,
                             badge_column: str | None = None, default_sort: str | None = None,
                             default_ascending: bool = False, height: int = 560) -> pd.DataFrame:
    """
    Renders a search box + sort controls + a glass-panel table with a
    sticky header and (optionally) a colored badge for `badge_column`.
    Returns the DataFrame actually displayed, so callers can feed the
    same filtered/sorted view into an export button.
    """
    if df.empty:
        render_html(
            f"""<div class="mi-glass mi-fade-in" style="padding:28px; text-align:center;
                color:{COLORS['muted']}; font-size:0.9rem;">No stocks found.</div>""",
        )
        return df

    search_columns = search_columns or list(df.columns)

    c1, c2, c3 = st.columns([2, 1.3, 0.7])
    with c1:
        query = st.text_input("🔍 Search stock", key=f"{key}_search", placeholder="Search by stock name...")
    with c2:
        sort_col = st.selectbox(
            "Sort by", options=list(df.columns),
            index=list(df.columns).index(default_sort) if default_sort in df.columns else 0,
            key=f"{key}_sort",
        )
    with c3:
        ascending = st.checkbox("Asc", value=default_ascending, key=f"{key}_asc")

    view = df.copy()
    if query:
        mask = pd.Series(False, index=view.index)
        for col in search_columns:
            if col in view.columns:
                mask |= view[col].astype(str).str.contains(query, case=False, na=False)
        view = view[mask]

    if sort_col in view.columns:
        view = view.sort_values(by=sort_col, ascending=ascending)

    if view.empty:
        render_html(
            f"""<div class="mi-glass" style="padding:24px; text-align:center;
                color:{COLORS['muted']}; font-size:0.88rem;">No matches for "{_html.escape(query)}".</div>""",
        )
        return view

    # Build the HTML table
    cols = list(view.columns)
    header_html = "".join(f"<th>{_html.escape(str(c))}</th>" for c in cols)

    rows_html = []
    for _, row in view.iterrows():
        cells = []
        for c in cols:
            val = row[c]
            if c == badge_column:
                cells.append(f"<td>{signal_badge_html(str(val))}</td>")
            elif isinstance(val, (int, float)):
                cells.append(f'<td class="mi-num">{val}</td>')
            else:
                cells.append(f"<td>{_html.escape(str(val))}</td>")
        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    render_html(
        f"""
        <style>
        .mi-badge {{
            display: inline-block; padding: 3px 10px; border-radius: 999px;
            font-size: 0.72rem; font-weight: 600; font-family: 'Inter', sans-serif;
            white-space: nowrap;
        }}
        .mi-table-wrap {{
            border: 1px solid {COLORS['border']}; border-radius: 14px;
            overflow: auto; max-height: {height}px;
            background: {COLORS['panel']};
        }}
        table.mi-table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; }}
        table.mi-table thead th {{
            position: sticky; top: 0; z-index: 2;
            background: {COLORS['panel_alt']}; color: {COLORS['muted']};
            text-align: left; padding: 10px 12px; font-weight: 600;
            font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.03em;
            border-bottom: 1px solid {COLORS['border_strong']};
        }}
        table.mi-table tbody td {{
            padding: 9px 12px; border-bottom: 1px solid {COLORS['border']};
            color: {COLORS['text']}; white-space: nowrap;
        }}
        table.mi-table tbody tr:hover {{ background: {COLORS['panel_alt']}; }}
        table.mi-table .mi-num {{ font-family: 'JetBrains Mono', monospace; }}
        </style>
        <div class="mi-table-wrap mi-fade-in">
            <table class="mi-table">
                <thead><tr>{header_html}</tr></thead>
                <tbody>{''.join(rows_html)}</tbody>
            </table>
        </div>
        <div style="color:{COLORS['faint']}; font-size:0.72rem; margin-top:6px;">
            Showing {len(view)} of {len(df)} stocks
        </div>
        """,
    )

    return view


# ======================================================================
# OPPORTUNITY CARD (SMA10 / EMA10 scanner detail card)
# ======================================================================

def render_opportunity_card(stock: str, market: str, price: float, ref_value: float,
                             ref_label: str, distance: float, status_label: str,
                             accent: str = "teal") -> str:
    color = COLORS.get(accent, COLORS["teal"])
    return f"""
    <div class="mi-opp-card mi-fade-in" style="--accent:{color}">
        <div class="mi-opp-top">
            <span class="mi-opp-stock">{_html.escape(stock)}</span>
            <span class="mi-opp-market">{_html.escape(market)}</span>
        </div>
        <div class="mi-opp-grid">
            <div><div class="mi-opp-k">Price</div><div class="mi-opp-v">{price}</div></div>
            <div><div class="mi-opp-k">{_html.escape(ref_label)}</div><div class="mi-opp-v">{ref_value}</div></div>
            <div><div class="mi-opp-k">Distance</div><div class="mi-opp-v" style="color:{color}">{distance}%</div></div>
        </div>
        <div class="mi-opp-status" style="color:{color}">{_html.escape(status_label)}</div>
    </div>
    """


def render_opportunity_grid(cards_html: list[str]) -> None:
    render_html(
        f"""
        <style>
        .mi-opp-grid-wrap {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 10px; margin: 10px 0;
        }}
        .mi-opp-card {{
            background: linear-gradient(180deg, {COLORS['panel']}, {COLORS['panel_alt']});
            border: 1px solid {COLORS['border']}; border-left: 3px solid var(--accent);
            border-radius: 12px; padding: 12px 14px;
            transition: transform 0.15s ease;
        }}
        .mi-opp-card:hover {{ transform: translateY(-2px); }}
        .mi-opp-top {{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:8px; }}
        .mi-opp-stock {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:0.95rem; color:{COLORS['text']}; }}
        .mi-opp-market {{ font-size:0.68rem; color:{COLORS['muted']}; text-transform:uppercase; letter-spacing:0.04em; }}
        .mi-opp-grid {{ display:flex; justify-content:space-between; gap:6px; margin-bottom:8px; }}
        .mi-opp-k {{ font-size:0.66rem; color:{COLORS['faint']}; text-transform:uppercase; }}
        .mi-opp-v {{ font-family:'JetBrains Mono',monospace; font-size:0.88rem; color:{COLORS['text']}; font-weight:500; }}
        .mi-opp-status {{ font-size:0.74rem; font-weight:600; }}
        </style>
        <div class="mi-opp-grid-wrap">{''.join(cards_html)}</div>
        """,
    )


# ======================================================================
# CHART PLACEHOLDERS (future-ready, no chart logic implemented yet)
# ======================================================================

def render_chart_placeholder(title: str, subtitle: str, kind: str = "line") -> None:
    """
    A styled placeholder panel reserving visual space + correct framing
    for a future chart (candlestick / SMA / EMA / RSI / Volume). Swap the
    inner div for a real plotting library call later — the container,
    spacing, and header stay identical.
    """
    icon = {"candlestick": "🕯️", "sma": "📈", "ema": "📉", "rsi": "📊", "volume": "📶"}.get(kind, "📈")
    render_html(
        f"""
        <style>
        .mi-chart-placeholder {{
            background: linear-gradient(180deg, {COLORS['panel']}, {COLORS['panel_alt']});
            border: 1px dashed {COLORS['border_strong']}; border-radius: 14px;
            padding: 30px 16px; text-align: center; margin: 10px 0;
        }}
        .mi-chart-icon {{ font-size: 1.8rem; opacity: 0.5; }}
        .mi-chart-title {{ font-family:'Space Grotesk',sans-serif; font-weight:600; color:{COLORS['text']}; margin-top:6px; }}
        .mi-chart-sub {{ color:{COLORS['muted']}; font-size:0.78rem; margin-top:2px; }}
        </style>
        <div class="mi-chart-placeholder mi-fade-in">
            <div class="mi-chart-icon">{icon}</div>
            <div class="mi-chart-title">{_html.escape(title)}</div>
            <div class="mi-chart-sub">{_html.escape(subtitle)} · coming soon</div>
        </div>
        """,
    )
