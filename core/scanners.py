"""
core/scanners.py

Purpose
-------
Pure filtering/bucketing over a list of already-computed analyzer results.
No fetching, no Streamlit — just list/DataFrame operations, so these are
trivially unit-testable.

Inputs
------
results: list[dict]  - output of core.analyzer.analyze_stock(), collected
                        across all stocks for the run.
threshold: float      - % distance cutoff (sidebar slider value)

Outputs
-------
sma10_scanner(results, threshold) -> list[dict]   # within threshold% of SMA10
ema_scanner(results) -> tuple[list[dict], list[dict]]  # (above, below)
bucket_by_signal(results) -> tuple[list, list, list]   # (bullish, neutral, bearish)

How it connects
----------------
app.py calls these once per market after collecting analyzer results, then
passes the lists into ui/tables.py for rendering and services/export_service.py
for Excel export.
"""


def sma10_scanner(results: list[dict], threshold: float) -> list[dict]:
    """Stocks whose Distance % from SMA10 is within `threshold`."""
    return [r for r in results if r["Distance %"] <= threshold]


def ema_scanner(results: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split results into (above EMA10, below EMA10) — same rule as original app."""
    above = [r for r in results if r["Close"] > r["EMA10"]]
    below = [r for r in results if r["Close"] <= r["EMA10"]]
    return above, below


def ema_scanner_within_threshold(results: list[dict], threshold: float) -> list[dict]:
    """
    Optional extra filter: EMA10 candidates within `threshold`% distance.
    Additive — does not change the above/below split used by the original tabs.
    """
    return [r for r in results if r["EMA Distance %"] <= threshold]


def bucket_by_signal(results: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """Split results into (bullish, neutral, bearish) buckets, same grouping as original app."""
    bullish = [r for r in results if r["Signal"] in ("🔥 Strong Bullish", "✅ Bullish")]
    neutral = [r for r in results if r["Signal"] == "➖ Neutral"]
    bearish = [r for r in results if r["Signal"] in ("⚠️ Bearish", "❌ Strong Bearish")]
    return bullish, neutral, bearish


def deduplicate(results: list[dict]) -> list[dict]:
    """Drop duplicate (Stock, Market) pairs, preserving first occurrence (matches original sma_df dedup)."""
    seen = set()
    deduped = []
    for r in results:
        key = (r["Stock"], r["Market"])
        if key not in seen:
            seen.add(key)
            deduped.append(r)
    return deduped


def group_by_sector(results: list[dict]) -> dict[str, list[dict]]:
    """
    Group a list of analyzer result dicts by their "Sector" field.
    Returns an ordered dict (alphabetical by sector name) so the sector
    tab renders consistently regardless of the order stocks were analyzed.
    Within each sector, stocks are sorted by Score descending (strongest
    signal first), matching the Indian/USA table sort convention.

    Input:  list of result dicts from core.analyzer.analyze_stock()
    Output: {sector_name: [result_dict, ...], ...}

    Coupling guarantee: the only thing this reads is r["Sector"] and
    r["Score"], both of which are always present in the analyzer output.
    Adding a new stock with a new sector in config/stocks_config.py makes
    that sector appear here automatically — no other file needs to change.
    """
    sectors: dict[str, list[dict]] = {}
    for r in results:
        sector = r.get("Sector", "Unknown")
        sectors.setdefault(sector, []).append(r)

    # Sort within each sector: highest score first
    for s in sectors:
        sectors[s].sort(key=lambda r: r.get("Score", 0), reverse=True)

    # Return alphabetically ordered sectors
    return dict(sorted(sectors.items()))
