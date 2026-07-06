"""
app.py

Purpose
-------
The thin orchestration layer for the "Market Intelligence Dashboard"
trading-terminal UI. Owns page config, theme injection, navigation, and
the run-analysis control flow. Contains zero indicator math, scoring
logic, or fetch/caching code — all of that lives untouched in core/ and
services/ exactly as before. This redesign only changes the presentation
layer (ui/).

Control surface
----------------
All run controls (Market, Date, SMA10/EMA10 thresholds, Run Analysis)
live in ONE place: the left sidebar (ui/sidebar.py). There is no
duplicate "Settings" tab — navigation only has the 9 content sections.
The sidebar starts expanded since it's the primary control surface, not
a secondary one.

How it connects
----------------
Imports from every layer (config, core, services, ui) — the only file
allowed to do so. Run with: streamlit run app.py
"""

from datetime import datetime

import pytz
import pandas as pd
import streamlit as st

from config.settings import PAGE_TITLE, PAGE_ICON, TIMEZONES
from config.stocks_config import INDIAN_STOCKS, USA_STOCKS, INDIA_INDEXES, USA_INDEXES
from core.analyzer import analyze_stock
from core.scanners import (
    sma10_scanner,
    ema_scanner,
    ema_scanner_within_threshold,
    bucket_by_signal,
    deduplicate,
    group_by_sector,
)
from services.export_service import export_india, export_usa, export_scanner
from services.notification_service import send_notification
from utils.helpers import is_market_open, build_date_fallback_note

from ui.theme import inject_theme, COLORS, render_html
from ui.components import (
    render_market_status,
    render_section_header,
    render_opportunity_card,
    render_opportunity_grid,
)
from ui.sidebar import render_sidebar_controls
from ui.dashboard import render_kpis
from ui.tables import render_results_section, render_download_button, to_dataframe
from ui.charts import render_signal_distribution, render_future_chart_gallery

# ==========================================================
# PAGE CONFIG + THEME
# ==========================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",  # the sidebar IS the control surface
)
inject_theme()

# ==========================================================
# HELPER FOR SIGNAL SORTING
# ==========================================================
def sort_by_signal_priority(df):
    """
    Enforces a strict categorical order on the dataframe based on Signal priority:
    Strong Bullish -> Bullish -> Neutral -> Bearish -> Strong Bearish
    """
    if df.empty or "Signal" not in df.columns:
        return df
        
    signal_order = [
        "🔥 Strong Bullish",
        "✅ Bullish",
        "➖ Neutral",
        "⚠️ Bearish",
        "❌ Strong Bearish"
    ]
    
    # Map any missing exact string matches just in case your code outputs slight variants
    df['Signal'] = df['Signal'].astype(str)
    
    # Create a categorical data type with the explicitly defined order
    df['Signal'] = pd.Categorical(df['Signal'], categories=signal_order, ordered=True)
    
    # Sort by Signal priority tier first, then sort by Score descending inside each tier
    return df.sort_values(by=["Signal", "Score"], ascending=[True, False]).reset_index(drop=True)

# ==========================================================
# SIDEBAR (the single control surface)
# ==========================================================

controls = render_sidebar_controls()

# ==========================================================
# TIME / MARKET STATUS
# ==========================================================

india_time = datetime.now(pytz.timezone(TIMEZONES["India"]))
usa_time = datetime.now(pytz.timezone(TIMEZONES["USA"]))

india_open = is_market_open(india_time, open_time=(9, 15), close_time=(15, 30))
usa_open = is_market_open(usa_time, open_time=(9, 30), close_time=(16, 0))

if controls["option"] == "Custom Date" and controls.get("custom_date"):
    selected_date_label = f"Custom ({controls['custom_date'].strftime('%d-%b-%Y')})"
else:
    selected_date_label = controls["option"]

render_market_status(
    india_open=india_open,
    usa_open=usa_open,
    ist_time=india_time.strftime("%I:%M:%S %p"),
    usa_time=usa_time.strftime("%I:%M:%S %p"),
    last_updated=st.session_state.get("mi_last_run_at", "—"),
    selected_date_label=selected_date_label,
)

# USA/India date-mismatch notice
for _note in st.session_state.get("mi_date_notes", []):
    st.info(f"ℹ️ {_note}")

# ==========================================================
# NAVIGATION (sticky pill tabs)
# ==========================================================

tab_dashboard, tab_india, tab_usa, tab_sma, tab_ema, tab_signals, tab_sectors, tab_ind_indexes, tab_usa_indexes = st.tabs(
    [
        "🏠 Dashboard",
        "🇮🇳 Indian Market",
        "🇺🇸 US Market",
        "🎯 SMA Scanner",
        "📈 EMA Scanner",
        "🔥 Signals",
        "🏭 Sectors",
        "📊 India Indexes",
        "🇺🇸 US Indexes",
    ]
)

run_clicked = controls["run_analysis"]

# ==========================================================
# RUN ANALYSIS
# ==========================================================

if run_clicked:
    run_india = controls["market"] in ("All", "India")
    run_usa = controls["market"] in ("All", "USA")

    stock_universe = []
    if run_india:
        stock_universe += [("India", name, info) for name, info in INDIAN_STOCKS.items()]
    if run_usa:
        stock_universe += [("USA", name, info) for name, info in USA_STOCKS.items()]

    with st.sidebar:
        progress_label = st.empty()
        progress_bar = st.progress(0)

    indian_results, usa_results = [], []
    total = max(len(stock_universe), 1)

    for i, (market_label, name, info) in enumerate(stock_universe, start=1):
        market_key = "INDIA" if market_label == "India" else "USA"
        result = analyze_stock(
            stock_name=name,
            symbol=info["symbol"],
            market=market_key,
            option=controls["option"],
            custom_date=controls["custom_date"],
            sector=info.get("sector", "N/A"),
        )
        progress_bar.progress(i / total)
        progress_label.caption(f"Analyzing {name}... ({i}/{total})")

        if result is None:
            continue

        (indian_results if market_label == "India" else usa_results).append(result)

    progress_label.empty()
    progress_bar.empty()

    # ------------------------------------------------------------------
    # INDIA INDEXES
    # ------------------------------------------------------------------
    index_results = []
    with st.sidebar:
        idx_label = st.empty()
        idx_bar = st.progress(0)

    idx_total = max(len(INDIA_INDEXES), 1)
    for idx_i, (idx_name, idx_info) in enumerate(INDIA_INDEXES.items(), start=1):
        idx_result = analyze_stock(
            stock_name=idx_name,
            symbol=idx_info["symbol"],
            market="INDIA",
            option=controls["option"],
            custom_date=controls["custom_date"],
            sector=idx_info.get("sector", "Index"),
        )
        idx_bar.progress(idx_i / idx_total)
        idx_label.caption(f"India Index: {idx_name}... ({idx_i}/{idx_total})")
        if idx_result is not None:
            index_results.append(idx_result)

    idx_label.empty()
    idx_bar.empty()

    # ------------------------------------------------------------------
    # USA INDEXES
    # ------------------------------------------------------------------
    usa_index_results = []
    with st.sidebar:
        usa_idx_label = st.empty()
        usa_idx_bar = st.progress(0)

    usa_idx_total = max(len(USA_INDEXES), 1)
    for u_idx_i, (u_idx_name, u_idx_info) in enumerate(USA_INDEXES.items(), start=1):
        u_idx_result = analyze_stock(
            stock_name=u_idx_name,
            symbol=u_idx_info["symbol"],
            market="USA",
            option=controls["option"],
            custom_date=controls["custom_date"],
            sector=u_idx_info.get("sector", "Index"),
        )
        usa_idx_bar.progress(u_idx_i / usa_idx_total)
        usa_idx_label.caption(f"USA Index: {u_idx_name}... ({u_idx_i}/{usa_idx_total})")
        if u_idx_result is not None:
            usa_index_results.append(u_idx_result)

    usa_idx_label.empty()
    usa_idx_bar.empty()

    all_results = indian_results + usa_results

    sma_results = deduplicate(sma10_scanner(all_results, controls["sma_threshold"]))
    ema_above_results, ema_below_results = ema_scanner(all_results)
    ema_opportunity_results = ema_scanner_within_threshold(all_results, controls["ema_threshold"])
    strong_bullish = [r for r in all_results if r["Signal"] == "🔥 Strong Bullish"]
    bullish_results, neutral_results, bearish_results = bucket_by_signal(all_results)

    st.session_state["mi_results"] = {
        "indian_results": indian_results,
        "usa_results": usa_results,
        "index_results": index_results,
        "usa_index_results": usa_index_results,
        "sma_results": sma_results,
        "ema_above_results": ema_above_results,
        "ema_below_results": ema_below_results,
        "ema_opportunity_results": ema_opportunity_results,
        "strong_bullish": strong_bullish,
        "bullish_results": bullish_results,
        "neutral_results": neutral_results,
        "bearish_results": bearish_results,
        "sectors": group_by_sector(all_results),
        "sma_threshold": controls["sma_threshold"],
        "ema_threshold": controls["ema_threshold"],
    }
    st.session_state["mi_last_run_at"] = india_time.strftime("%I:%M:%S %p IST")

    india_note = build_date_fallback_note(controls["option"], controls["custom_date"], indian_results, "🇮🇳 India")
    usa_note = build_date_fallback_note(controls["option"], controls["custom_date"], usa_results, "🇺🇸 USA")
    st.session_state["mi_date_notes"] = [n for n in (india_note, usa_note) if n]

    send_notification(
        f"Analysis run complete: {len(bullish_results)} bullish, "
        f"{len(neutral_results)} neutral, {len(bearish_results)} bearish."
    )

# ==========================================================
# READ LAST RESULTS
# ==========================================================

results = st.session_state.get("mi_results")

if not results:
    with tab_dashboard:
        render_html(
            f"""
            <div class="mi-glass mi-fade-in" style="padding:40px 24px; text-align:center; margin-top:10px;">
                <div style="font-size:2rem;">🚀</div>
                <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.1rem;
                            color:{COLORS['text']}; margin-top:8px;">No scan yet</div>
                <div style="color:{COLORS['muted']}; font-size:0.85rem; margin-top:4px;">
                    Use the panel on the left and tap <b>Run Analysis</b> to populate the dashboard.
                </div>
            </div>
            """,
        )
    st.stop()

# ==========================================================
# DASHBOARD TAB
# ==========================================================

with tab_dashboard:
    counts = {
        "total": len(results["indian_results"]) + len(results["usa_results"]),
        "strong_bullish": len(results["strong_bullish"]),
        "bullish": len(results["bullish_results"]),
        "neutral": len(results["neutral_results"]),
        "bearish": len(results["bearish_results"]),
        "sma10": len(results["sma_results"]),
        "ema10": len(results["ema_opportunity_results"]),
    }
    render_kpis(counts)
    render_signal_distribution(
        {
            "Strong Bullish": counts["strong_bullish"],
            "Bullish": len(results["bullish_results"]) - counts["strong_bullish"],
            "Neutral": counts["neutral"],
            "Bearish": sum(1 for r in results["bearish_results"] if r["Signal"] == "⚠️ Bearish"),
            "Strong Bearish": sum(1 for r in results["bearish_results"] if r["Signal"] == "❌ Strong Bearish"),
        }
    )
    render_future_chart_gallery()

# ==========================================================
# INDIAN MARKET TAB
# ==========================================================

with tab_india:
    indian_df = render_results_section(
        "🇮🇳", "Indian Stocks Analysis", "All NSE stocks in the configured universe",
        results["indian_results"], key="india",
    )
    if not indian_df.empty:
        # Categorically sort the DataFrame right before giving it to Excel export
        sorted_indian_df = sort_by_signal_priority(indian_df.copy())
        c1, _ = st.columns([1, 3])
        render_download_button(c1, "📥 Export India", sorted_indian_df, "india_stocks.xlsx", export_india)

# ==========================================================
# US MARKET TAB
# ==========================================================

with tab_usa:
    usa_df = render_results_section(
        "🇺🇸", "USA Stocks Analysis", "All US-listed stocks in the configured universe",
        results["usa_results"], key="usa",
    )
    if not usa_df.empty:
        # Categorically sort the DataFrame right before giving it to Excel export
        sorted_usa_df = sort_by_signal_priority(usa_df.copy())
        c1, _ = st.columns([1, 3])
        render_download_button(c1, "📥 Export USA", sorted_usa_df, "usa_stocks.xlsx", export_usa)

# ==========================================================
# SMA10 SCANNER TAB
# ==========================================================

with tab_sma:
    render_section_header(
        "🎯", "SMA10 Opportunity Scanner",
        f"Stocks within {results['sma_threshold']}% of their 10-day SMA",
    )

    sma_df = to_dataframe(results["sma_results"])
    if sma_df.empty:
        render_html(
            f"""<div class="mi-glass" style="padding:24px; text-align:center; color:{COLORS['muted']};">
                No stocks found near SMA10 at this threshold. Try widening it in the left panel.</div>""",
        )
    else:
        ranked = sma_df.sort_values(by="Distance %", ascending=True)
        st.caption(f"{len(ranked)} opportunities, ranked by proximity to SMA10")

        cards = []
        for _, r in ranked.iterrows():
            status = "Near Support" if r["Side"] == "Above SMA10" else "Near Resistance"
            accent = "green" if r["Side"] == "Above SMA10" else "orange"
            cards.append(render_opportunity_card(
                stock=r["Stock"], market=r["Market"], price=r["Close"],
                ref_value=r["SMA10"], ref_label="SMA10", distance=r["Distance %"],
                status_label=f"● {status}", accent=accent,
            ))
        render_opportunity_grid(cards)

        c1, _ = st.columns([1, 3])
        render_download_button(c1, "📥 Export Scanner", sma_df, "sma_scanner.xlsx", export_scanner)

# ==========================================================
# EMA10 SCANNER TAB
# ==========================================================

with tab_ema:
    render_section_header("📈", "EMA10 Trend Scanner", "Momentum (above) vs reversal-watch (below) candidates")

    above_df = to_dataframe(results["ema_above_results"]).sort_values(by="EMA Distance %", ascending=True) \
        if results["ema_above_results"] else to_dataframe(results["ema_above_results"])
    below_df = to_dataframe(results["ema_below_results"]).sort_values(by="EMA Distance %", ascending=True) \
        if results["ema_below_results"] else to_dataframe(results["ema_below_results"])

    st.markdown(f"**🟢 Above EMA10** — momentum stocks ({len(above_df)})")
    if above_df.empty:
        st.caption("No stocks currently above EMA10.")
    else:
        cards = [
            render_opportunity_card(
                stock=r["Stock"], market=r["Market"], price=r["Close"],
                ref_value=r["EMA10"], ref_label="EMA10", distance=r["EMA Distance %"],
                status_label="● Momentum", accent="green",
            )
            for _, r in above_df.head(20).iterrows()
        ]
        render_opportunity_grid(cards)

    st.markdown(f"**🔴 Below EMA10** — possible reversal watch ({len(below_df)})")
    if below_df.empty:
        st.caption("No stocks currently below EMA10.")
    else:
        cards = [
            render_opportunity_card(
                stock=r["Stock"], market=r["Market"], price=r["Close"],
                ref_value=r["EMA10"], ref_label="EMA10", distance=r["EMA Distance %"],
                status_label="● Reversal Watch", accent="red",
            )
            for _, r in below_df.head(20).iterrows()
        ]
        render_opportunity_grid(cards)

# ==========================================================
# SIGNALS TAB
# ==========================================================

with tab_signals:
    render_section_header("🔥", "Signal Explorer", "Bullish, Neutral, and Bearish buckets in one place")

    bucket_choice = st.radio(
        "Bucket", ["🔥 Bullish", "➖ Neutral", "⚠️ Bearish"], horizontal=True,
        label_visibility="collapsed", key="signals_bucket",
    )

    if bucket_choice == "🔥 Bullish":
        bucket_df = render_results_section(
            "🔥", "Bullish Stocks", "Strong Bullish + Bullish signals",
            results["bullish_results"], key="bullish", default_sort="Score", default_ascending=False,
        )
        file_name = "bullish_stocks.xlsx"
    elif bucket_choice == "➖ Neutral":
        bucket_df = render_results_section(
            "➖", "Neutral Stocks", "No clear directional edge",
            results["neutral_results"], key="neutral", default_sort="Score", default_ascending=False,
        )
        file_name = "neutral_stocks.xlsx"
    else:
        bucket_df = render_results_section(
            "⚠️", "Bearish Stocks", "Bearish + Strong Bearish signals",
            results["bearish_results"], key="bearish", default_sort="Score", default_ascending=True,
        )
        file_name = "bearish_stocks.xlsx"

    if not bucket_df.empty:
        # Enforce signal ranking within exported specific view buckets too
        sorted_bucket_df = sort_by_signal_priority(bucket_df.copy())
        c1, _ = st.columns([1, 3])
        render_download_button(c1, "📥 Export Bucket", sorted_bucket_df, file_name, export_scanner)

# ==========================================================
# SECTORS TAB
# ==========================================================

with tab_sectors:
    render_section_header(
        "🏭", "Sector Analysis",
        "Stocks grouped by sector — coupled to config/stocks_config.py",
    )

    if not results:
        render_html(
            f"""<div class="mi-glass mi-fade-in" style="padding:32px 20px; text-align:center;">
            <div style="font-size:1.8rem;">🏭</div>
            <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; color:{COLORS['text']}; margin-top:6px;">
            Run a scan first</div>
            <div style="color:{COLORS['muted']}; font-size:0.83rem; margin-top:4px;">
            Sector data is derived from the scan results — use the left panel to start one.</div>
            </div>""",
        )
    else:
        sectors = results.get("sectors", {})

        if not sectors:
            st.caption("No sector data found — make sure stocks in config/stocks_config.py have a 'sector' key.")
        else:
            chip_parts = []
            for sec_name, sec_stocks in sectors.items():
                bullish_n = sum(1 for r in sec_stocks if r["Signal"] in ("🔥 Strong Bullish", "✅ Bullish"))
                bearish_n = sum(1 for r in sec_stocks if r["Signal"] in ("⚠️ Bearish", "❌ Strong Bearish"))
                if bullish_n > bearish_n:
                    chip_color = COLORS["green"]
                elif bearish_n > bullish_n:
                    chip_color = COLORS["red"]
                else:
                    chip_color = COLORS["amber"]
                chip_parts.append(
                    f'<span style="display:inline-flex;align-items:center;gap:5px;'
                    f'background:{COLORS["panel_alt"]};border:1px solid {chip_color}55;'
                    f'border-radius:999px;padding:5px 12px;font-size:0.75rem;margin:3px;">'
                    f'<span style="color:{chip_color};font-weight:700;">{sec_name}</span>'
                    f'<span style="color:{COLORS["muted"]};">{len(sec_stocks)}</span></span>'
                )
            render_html(
                f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:16px;">'
                f'{"".join(chip_parts)}</div>',
            )

            for sec_name, sec_stocks in sectors.items():
                bullish_n = sum(1 for r in sec_stocks if r["Signal"] in ("🔥 Strong Bullish", "✅ Bullish"))
                bearish_n = sum(1 for r in sec_stocks if r["Signal"] in ("⚠️ Bearish", "❌ Strong Bearish"))
                neutral_n = len(sec_stocks) - bullish_n - bearish_n

                label = (
                    f"{sec_name}  ·  {len(sec_stocks)} stocks  |  "
                    f"🟢 {bullish_n}  ➖ {neutral_n}  🔴 {bearish_n}"
                )
                with st.expander(label, expanded=False):
                    sec_df = to_dataframe(sec_stocks)
                    from ui.tables import to_display_view
                    from ui.components import render_searchable_table
                    render_searchable_table(
                        to_display_view(sec_df),
                        key=f"sector_{sec_name.replace(' ', '_').replace('/', '_')}",
                        search_columns=["Stock", "Market"],
                        badge_column="Signal",
                        default_sort="Score",
                        default_ascending=False,
                    )

# ==========================================================
# INDIA INDEXES TAB
# ==========================================================

with tab_ind_indexes:
    render_section_header(
        "📊", "India Indexes",
        "NSE broad-market and sectoral indices — same SMA/EMA/RSI scoring as stocks",
    )

    if not results:
        render_html(
            f"""<div class="mi-glass mi-fade-in" style="padding:32px 20px; text-align:center;">
            <div style="font-size:1.8rem;">📊</div>
            <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; color:{COLORS['text']}; margin-top:6px;">
            Run a scan first</div>
            <div style="color:{COLORS['muted']}; font-size:0.83rem; margin-top:4px;">
            Index data is fetched alongside the main scan.</div>
            </div>""",
        )
    else:
        idx_results = results.get("index_results", [])
        if not idx_results:
            render_html(
                f"""<div class="mi-glass" style="padding:24px; text-align:center; color:{COLORS['muted']};">
                No index data available. Yahoo Finance may not have returned data for some symbols.</div>""",
            )
        else:
            idx_df = render_results_section(
                "📊", "NSE Indices Analysis",
                f"{len(idx_results)} of {len(INDIA_INDEXES)} indices fetched successfully",
                idx_results, key="indexes",
                default_sort="Score", default_ascending=False,
            )
            
            idx_bull = sum(1 for r in idx_results if r["Signal"] in ("🔥 Strong Bullish", "✅ Bullish"))
            idx_neu  = sum(1 for r in idx_results if r["Signal"] == "➖ Neutral")
            idx_bear = sum(1 for r in idx_results if r["Signal"] in ("⚠️ Bearish", "❌ Strong Bearish"))
            render_html(
                f"""<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:14px;">
                <div style="flex:1;min-width:130px;background:{COLORS['panel']};border:1px solid {COLORS['green']}44;
                border-left:3px solid {COLORS['green']};border-radius:10px;padding:12px 14px;">
                <div style="color:{COLORS['muted']};font-size:0.7rem;text-transform:uppercase;">Bullish Indices</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;
                color:{COLORS['green']};">{idx_bull}</div></div>
                <div style="flex:1;min-width:130px;background:{COLORS['panel']};border:1px solid {COLORS['amber']}44;
                border-left:3px solid {COLORS['amber']};border-radius:10px;padding:12px 14px;">
                <div style="color:{COLORS['muted']};font-size:0.7rem;text-transform:uppercase;">Neutral Indices</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;
                color:{COLORS['amber']};">{idx_neu}</div></div>
                <div style="flex:1;min-width:130px;background:{COLORS['panel']};border:1px solid {COLORS['red']}44;
                border-left:3px solid {COLORS['red']};border-radius:10px;padding:12px 14px;">
                <div style="color:{COLORS['muted']};font-size:0.7rem;text-transform:uppercase;">Bearish Indices</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;
                color:{COLORS['red']};">{idx_bear}</div></div>
                </div>""",
            )
            if not idx_df.empty:
                # Also sort index sheets categorically by signal
                sorted_idx_df = sort_by_signal_priority(idx_df.copy())
                c1, _ = st.columns([1, 3])
                render_download_button(c1, "📥 Export Indexes", sorted_idx_df, "india_indexes.xlsx", export_scanner)

# ==========================================================
# US INDEXES TAB
# ==========================================================

with tab_usa_indexes:
    render_section_header(
        "🇺🇸", "US Indexes",
        "US major indices and key market-sector ETFs — same SMA/EMA/RSI scoring as stocks",
    )

    if not results:
        render_html(
            f"""<div class="mi-glass mi-fade-in" style="padding:32px 20px; text-align:center;">
            <div style="font-size:1.8rem;">🇺🇸</div>
            <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; color:{COLORS['text']}; margin-top:6px;">
            Run a scan first</div>
            <div style="color:{COLORS['muted']}; font-size:0.83rem; margin-top:4px;">
            US index data is fetched alongside the main scan.</div>
            </div>""",
        )
    else:
        usa_idx_results = results.get("usa_index_results", [])
        if not usa_idx_results:
            render_html(
                f"""<div class="mi-glass" style="padding:24px; text-align:center; color:{COLORS['muted']};">
                No US index data available. Yahoo Finance may not have returned data for some symbols.</div>""",
            )
        else:
            usa_idx_df = render_results_section(
                "🇺🇸", "US Indices Analysis",
                f"{len(usa_idx_results)} of {len(USA_INDEXES)} indices fetched successfully",
                usa_idx_results, key="usa_indexes",
                default_sort="Score", default_ascending=False,
            )
            
            u_idx_bull = sum(1 for r in usa_idx_results if r["Signal"] in ("🔥 Strong Bullish", "✅ Bullish"))
            u_idx_neu  = sum(1 for r in usa_idx_results if r["Signal"] == "➖ Neutral")
            u_idx_bear = sum(1 for r in usa_idx_results if r["Signal"] in ("⚠️ Bearish", "❌ Strong Bearish"))
            render_html(
                f"""<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:14px;">
                <div style="flex:1;min-width:130px;background:{COLORS['panel']};border:1px solid {COLORS['green']}44;
                border-left:3px solid {COLORS['green']};border-radius:10px;padding:12px 14px;">
                <div style="color:{COLORS['muted']};font-size:0.7rem;text-transform:uppercase;">Bullish US Indices</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;
                color:{COLORS['green']};">{u_idx_bull}</div></div>
                <div style="flex:1;min-width:130px;background:{COLORS['panel']};border:1px solid {COLORS['amber']}44;
                border-left:3px solid {COLORS['amber']};border-radius:10px;padding:12px 14px;">
                <div style="color:{COLORS['muted']};font-size:0.7rem;text-transform:uppercase;">Neutral US Indices</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;
                color:{COLORS['amber']};">{u_idx_neu}</div></div>
                <div style="flex:1;min-width:130px;background:{COLORS['panel']};border:1px solid {COLORS['red']}44;
                border-left:3px solid {COLORS['red']};border-radius:10px;padding:12px 14px;">
                <div style="color:{COLORS['muted']};font-size:0.7rem;text-transform:uppercase;">Bearish US Indices</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;
                color:{COLORS['red']};">{u_idx_bear}</div></div>
                </div>""",
            )
            if not usa_idx_df.empty:
                # Also sort US index sheets categorically by signal
                sorted_usa_idx_df = sort_by_signal_priority(usa_idx_df.copy())
                c1, _ = st.columns([1, 3])
                render_download_button(c1, "📥 Export US Indexes", sorted_usa_idx_df, "usa_indexes.xlsx", export_scanner)

# ==========================================================
# END
# ==========================================================