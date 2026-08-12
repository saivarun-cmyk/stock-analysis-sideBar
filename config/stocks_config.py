"""
config/stocks_config.py

Purpose
-------
The ONLY file you should ever need to edit to add, remove, or re-categorize
a stock. Nothing in core/, services/, or ui/ has stock names hard-coded.

Inputs
------
None.

Outputs
-------
INDIAN_STOCKS: dict[str, dict] -> {"DisplayName": {"symbol": "TCS.NS", "sector": "IT"}}
USA_STOCKS:    dict[str, dict] -> {"DisplayName": {"symbol": "NVDA", "sector": "Technology"}}

How it connects
----------------
app.py iterates over these dicts and calls core.analyzer.analyze_stock(name, symbol, market, ...)
for every entry. The "symbol" field here is already the final Yahoo Finance
ticker (".NS" suffix already applied for NSE stocks, "^NSEI" for the index),
so core/data_fetcher.py does not need to guess suffixes — it trusts this config.

To add a new stock:
    1. Pick a display name (used as the row label everywhere in the UI).
    2. Add the correct Yahoo Finance ticker as "symbol".
    3. Add a "sector" (purely informational, shown in tables).
That's it — no other file needs to change.
"""

INDIAN_STOCKS = {
    # Original Stocks
    "M&M": {"symbol": "M&M.NS", "sector": "Automobile"},
    "Hero Motocorp": {"symbol": "HEROMOTOCO.NS", "sector": "Automobile"},
    "KPIT Technology": {"symbol": "KPITTECH.NS", "sector": "IT"},
    "LTM": {"symbol": "LTM.NS", "sector": "IT"},
    "Mphasis": {"symbol": "MPHASIS.NS", "sector": "IT"},
    "Maruti": {"symbol": "MARUTI.NS", "sector": "Automobile"},
    "DLF": {"symbol": "DLF.NS", "sector": "Realty"},
    "Dixon": {"symbol": "DIXON.NS", "sector": "Electronics"},
    "SHRIRAM Finance": {"symbol": "SHRIRAMFIN.NS", "sector": "Finance"},
    "Indigo": {"symbol": "INDIGO.NS", "sector": "Aviation"},
    "Eicher Motors": {"symbol": "EICHERMOT.NS", "sector": "Automobile"},
    "Bajaj Auto": {"symbol": "BAJAJ-AUTO.NS", "sector": "Automobile"},
    "VEDL": {"symbol": "VEDL.NS", "sector": "Metals"},
    "HAL": {"symbol": "HAL.NS", "sector": "Defence"},
    "JSW Steel": {"symbol": "JSWSTEEL.NS", "sector": "Metals"},
    "LT": {"symbol": "LT.NS", "sector": "Infrastructure"},
    "SBIN": {"symbol": "SBIN.NS", "sector": "Banking"},
    "Persistent Systems": {"symbol": "PERSISTENT.NS", "sector": "IT"},
    "Tata Steel": {"symbol": "TATASTEEL.NS", "sector": "Metals"},
    "BHEL": {"symbol": "BHEL.NS", "sector": "Capital Goods"},
    "ABB": {"symbol": "ABB.NS", "sector": "Capital Goods"},
    "Siemens": {"symbol": "SIEMENS.NS", "sector": "Capital Goods"},
    "NTPC": {"symbol": "NTPC.NS", "sector": "Power"},
    "National Aluminium": {"symbol": "NATIONALUM.NS", "sector": "Metals"},
    "Kaynes": {"symbol": "KAYNES.NS", "sector": "Electronics"},
    "MCX": {"symbol": "MCX.NS", "sector": "Finance"},
    "BSE": {"symbol": "BSE.NS", "sector": "Finance"},
    "Trent": {"symbol": "TRENT.NS", "sector": "Retail"},
    "Asian Paints": {"symbol": "ASIANPAINT.NS", "sector": "Consumer"},
    "OFSS": {"symbol": "OFSS.NS", "sector": "IT"},
    "Hindalco": {"symbol": "HINDALCO.NS", "sector": "Metals"},
    "Cummins India": {"symbol": "CUMMINSIND.NS", "sector": "Capital Goods"},
    "TCS": {"symbol": "TCS.NS", "sector": "IT"},
    "Infosys": {"symbol": "INFY.NS", "sector": "IT"},
    "Tata Elxsi": {"symbol": "TATAELXSI.NS", "sector": "IT"},
    "Bajaj Finance": {"symbol": "BAJFINANCE.NS", "sector": "Finance"},
    "Polycab": {"symbol": "POLYCAB.NS", "sector": "Electronics"},
    "ICICI Bank": {"symbol": "ICICIBANK.NS", "sector": "Banking"},
    "Lupin": {"symbol": "LUPIN.NS", "sector": "Pharma"},
    "Laurus Labs": {"symbol": "LAURUSLABS.NS", "sector": "Pharma"},
    "NIFTY 50": {"symbol": "^NSEI", "sector": "Index"},

    # Newly Added Stocks
    "PFC": {"symbol": "PFC.NS", "sector": "Finance"},
    "REC": {"symbol": "RECLTD.NS", "sector": "Finance"},
    "Force Motors": {"symbol": "FORCEMOT.NS", "sector": "Automobile"},
    "Oil India": {"symbol": "OIL.NS", "sector": "Energy"},
    "Coforge": {"symbol": "COFORGE.NS", "sector": "IT"},
    "Tech Mahindra": {"symbol": "TECHM.NS", "sector": "IT"},
    "HCL Tech": {"symbol": "HCLTECH.NS", "sector": "IT"},
    "CDSL": {"symbol": "CDSL.NS", "sector": "Finance"},
    "Mankind Pharma": {"symbol": "MANKIND.NS", "sector": "Pharma"},
    "Voltas": {"symbol": "VOLTAS.NS", "sector": "Consumer Electronics"},
    "Power India": {"symbol": "POWERINDIA.NS", "sector": "Capital Goods"},
    "Titan": {"symbol": "TITAN.NS", "sector": "Consumer Discretionary"},
    "Kalyan Jewellers": {"symbol": "KALYANKJIL.NS", "sector": "Consumer Discretionary"},
    "ONGC": {"symbol": "ONGC.NS", "sector": "Energy"},
    "BPCL": {"symbol": "BPCL.NS", "sector": "Energy"},
    "Suzlon": {"symbol": "SUZLON.NS", "sector": "Energy"},
    "ITC": {"symbol": "ITC.NS", "sector": "FMCG"},
    "Britannia": {"symbol": "BRITANNIA.NS", "sector": "FMCG"},
    "Premier Energies": {"symbol": "PREMIERENE.NS", "sector": "Energy"},
    "Glenmark Pharma": {"symbol": "GLENMARK.NS", "sector": "Pharma"},
    "Nestle India": {"symbol": "NESTLEIND.NS", "sector": "FMCG"},
    "Godrej Properties": {"symbol": "GODREJPROP.NS", "sector": "Realty"},
    "Apollo Hospitals": {"symbol": "APOLLOHOSP.NS", "sector": "Healthcare"},
}

USA_STOCKS = {
    "AAPL": {"symbol": "AAPL", "sector": "Technology"},
    "ABBV": {"symbol": "ABBV", "sector": "Pharma"},
    "AMAT": {"symbol": "AMAT", "sector": "Semiconductors"},
    "AMD": {"symbol": "AMD", "sector": "Semiconductors"},
    "AMZN": {"symbol": "AMZN", "sector": "Consumer"},
    "AVGO": {"symbol": "AVGO", "sector": "Semiconductors"},
    "AXP": {"symbol": "AXP", "sector": "Finance"},
    "BA": {"symbol": "BA", "sector": "Aerospace"},
    "BAC": {"symbol": "BAC", "sector": "Banking"},
    "CAT": {"symbol": "CAT", "sector": "Industrials"},
    "COST": {"symbol": "COST", "sector": "Retail"},
    "DELL": {"symbol": "DELL", "sector": "IT"},
    "GE": {"symbol": "GE", "sector": "Industrial"},
    "GOOGL": {"symbol": "GOOGL", "sector": "Technology"},
    "GS": {"symbol": "GS", "sector": "Finance"},
    "HD": {"symbol": "HD", "sector": "Retail"},
    "IBM": {"symbol": "IBM", "sector": "IT"},
    "JNJ": {"symbol": "JNJ", "sector": "Pharma"},
    "JPM": {"symbol": "JPM", "sector": "Finance"},
    "LLY": {"symbol": "LLY", "sector": "Pharma"},
    "LRCX": {"symbol": "LRCX", "sector": "Semiconductors"},
    "META": {"symbol": "META", "sector": "Technology"},
    "MSFT": {"symbol": "MSFT", "sector": "Technology"},
    "MU": {"symbol": "MU", "sector": "Semiconductors"},
    "NVDA": {"symbol": "NVDA", "sector": "Semiconductors"},
    "PG": {"symbol": "PG", "sector": "Consumer"},
    "PLTR": {"symbol": "PLTR", "sector": "IT"},
    "TSLA": {"symbol": "TSLA", "sector": "Automobile"},
    "UNH": {"symbol": "UNH", "sector": "Healthcare"},
    "V": {"symbol": "V", "sector": "Finance"},
    "WMT": {"symbol": "WMT", "sector": "Retail"},
    "XOM": {"symbol": "XOM", "sector": "Energy"},
}

# ======================================================================
# INDIA INDEXES
# ======================================================================
# Broad market indices tracked by NSE.  Adding a new index here is all
# that's required for it to appear in the "India Indexes" tab — no other
# file needs to change.  Symbols are Yahoo Finance index tickers (all
# start with ^, so core/data_fetcher.build_ticker passes them straight
# through without appending .NS).
#
# A handful of newer NSE thematic indices are NOT on Yahoo Finance at
# all (Yahoo only has the underlying ETFs that track them, not the raw
# index). For those, the "symbol" uses the "NSE:<INDEX NAME>" format,
# which core/data_fetcher.py should route to the nselib fallback instead
# of Yahoo — same pattern already used for "Nifty Ind Defence" below.
# ======================================================================


INDIA_INDEXES = {
    # Your existing working indexes
    "Nifty 50":           {"symbol": "^NSEI",       "sector": "Broad Market"},
    "Bank Nifty":         {"symbol": "^NSEBANK",    "sector": "Banking"},
    "Nifty IT":           {"symbol": "^CNXIT",      "sector": "IT"},
    "Nifty Metal":        {"symbol": "^CNXMETAL",   "sector": "Metals"},
    "Nifty Finance":      {"symbol": "^CNXFIN",     "sector": "Finance"},
    "Nifty Auto":         {"symbol": "^CNXAUTO",    "sector": "Automobile"},
    "Nifty Pharma":       {"symbol": "^CNXPHARMA",  "sector": "Pharma"},
    "Nifty Infra":        {"symbol": "^CNXINFRA",   "sector": "Infrastructure"},
    "Nifty Realty":       {"symbol": "^CNXREALTY",  "sector": "Realty"},
    "Nifty Energy":       {"symbol": "^CNXENERGY",  "sector": "Energy"},
    "Nifty FMCG":         {"symbol": "^CNXFMCG",    "sector": "FMCG"},

    # Your newly added custom nselib indexes.
    # NOTE: nseindia.com aggressively blocks requests from cloud-hosted apps
    # (Streamlit Cloud etc.) -- the NSE: fallback can silently return no data
    # for reasons entirely outside this code (see comment block below).
    # "Nifty Oil and Gas" IS available directly on Yahoo Finance under its
    # own raw index ticker, so it no longer needs the NSE: fallback at all.
    "Nifty Oil and Gas":  {"symbol": "NIFTY_OIL_AND_GAS.NS", "sector": "Energy"},
    # "Nifty India Defence" has no raw index ticker on Yahoo -- using the
    # Motilal Oswal ETF that tracks it as a reliable proxy instead. This
    # tracks the index closely but is NOT the exact index level (ETF price,
    # not index points) -- fine for trend/signal purposes, not exact levels.
    "Nifty Ind Defence":  {"symbol": "MODEFENCE.NS", "sector": "Defence"},

    # ------------------------------------------------------------------
    # Thematic radar (added per request)
    # ------------------------------------------------------------------
    # These four ARE on Yahoo Finance under their own raw .NS index tickers
    # (confirmed via Yahoo Finance's own historical-data pages) -- far more
    # reliable than scraping nseindia.com from a cloud host.
    "Nifty Capital Markets":       {"symbol": "NIFTY_CAPITAL_MKT.NS", "sector": "Finance"},
    "Nifty India Digital":         {"symbol": "NIFTY_IND_DIGITAL.NS", "sector": "Digital Economy"},
    "Nifty India Manufacturing":   {"symbol": "NIFTY_INDIA_MFG.NS",   "sector": "Manufacturing"},
    # No raw Yahoo index ticker exists for "Nifty EV & New Age Automotive" --
    # using the Mirae Asset ETF that tracks it (same proxy caveat as above).
    "Nifty EV & New Age Automotive": {"symbol": "EVINDIA.NS", "sector": "EV/Automobile"},

    # These three have NEITHER a raw Yahoo index ticker NOR a confirmed
    # tracking ETF on Yahoo yet (all are recently-launched NSE thematic
    # indices, June 2025 or later) -- they stay on the nselib "NSE:" fallback.
    # If they still come back empty after the & -> %26 encoding fix, that's
    # nseindia.com blocking the request at the network level, not a bug here
    # -- check the app logs for "NSE fetch failed" / "NSE fetch returned no
    # rows" to confirm before assuming it's fixable in code.
    "Nifty India Internet":                    {"symbol": "NSE:NIFTY INDIA INTERNET",                   "sector": "Internet/Digital"},
    "Nifty India Infrastructure & Logistics":  {"symbol": "NSE:NIFTY INDIA INFRASTRUCTURE & LOGISTICS", "sector": "Infrastructure"},
    "Nifty India New Age Consumption":         {"symbol": "NSE:NIFTY INDIA NEW AGE CONSUMPTION",        "sector": "Consumption"},
}

USA_INDEXES = {
    "S&P 500":        {"symbol": "^GSPC", "sector": "Broad Market"},
    "Nasdaq 100":     {"symbol": "QQQ",   "sector": "Technology & Growth"},
    "Russell 2000":   {"symbol": "IWM",   "sector": "Small Cap"},
    "Semiconductor":  {"symbol": "SOXX",  "sector": "Semiconductors"},
    "Technology":     {"symbol": "XLK",   "sector": "Technology"},
    "Financial":      {"symbol": "XLF",   "sector": "Finance"},
    "Consumer Disc":  {"symbol": "XLY",   "sector": "Consumer Discretionary"},
    "Consumer Staples":{"symbol": "XLP",  "sector": "Consumer Staples"},
    "Healthcare":     {"symbol": "XLV",   "sector": "Healthcare"},
    "Industrial":     {"symbol": "XLI",   "sector": "Industrials"},
    "Energy":         {"symbol": "XLE",   "sector": "Energy"},
    "Communication":  {"symbol": "XLC",   "sector": "Communication Services"},
    "Materials":      {"symbol": "XLB",   "sector": "Materials"},

    # ------------------------------------------------------------------
    # US THEMATIC (added per request) — all confirmed on Yahoo Finance,
    # no suffix needed since they're plain NYSE/Nasdaq-listed ETFs.
    # ------------------------------------------------------------------
    "Internet":            {"symbol": "FDN",  "sector": "Internet"},
    "FinTech":              {"symbol": "FINX", "sector": "FinTech"},
    "Artificial Intelligence": {"symbol": "AIQ", "sector": "Artificial Intelligence"},
    "Cybersecurity":        {"symbol": "CIBR", "sector": "Cybersecurity"},
    "Cloud Computing":      {"symbol": "SKYY", "sector": "Cloud Computing"},
    "Aerospace & Defence":  {"symbol": "ITA",  "sector": "Aerospace & Defence"},
    "Infrastructure":       {"symbol": "PAVE", "sector": "Infrastructure"},
    "Uranium & Nuclear":    {"symbol": "URA",  "sector": "Uranium/Nuclear"},
    "Biotechnology":        {"symbol": "XBI",  "sector": "Biotechnology"},
    # Note: SMH (semiconductors) intentionally skipped — you already have
    # SOXX above and the ChatGPT thread flagged them as redundant.
}
