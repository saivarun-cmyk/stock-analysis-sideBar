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
    "M&M": {"symbol": "M&M.NS", "sector": "Automobile"},
    "Hero Motocorp": {"symbol": "HEROMOTOCO.NS", "sector": "Automobile"},
    "KPIT Technology": {"symbol": "KPITTECH.NS", "sector": "IT"},
    "LTM": {"symbol": "LTIM.NS", "sector": "IT"},
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
# ======================================================================

INDIA_INDEXES = {
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
    "Nifty FMCG":         {"symbol": "^CNXFMCG",   "sector": "FMCG"},
    "Nifty Defence":      {"symbol": "^CNXDEFENCE", "sector": "Defence"},
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
}
