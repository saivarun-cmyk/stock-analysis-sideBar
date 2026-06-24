"""
ui/theme.py

Purpose
-------
The single source of visual identity: design tokens (colors, fonts) and
the CSS that turns Streamlit's default chrome into the "Market
Intelligence" trading-terminal look. Nothing here touches business logic
— it only injects <style> via st.markdown, mobile-first.

Inputs
------
None.

Outputs
-------
inject_theme() -> None  (writes <style>/<link> tags into the page)
COLORS: dict[str, str]  - token palette, reused by ui/components.py for
                          inline styles that can't live in static CSS
                          (e.g. dynamically picked signal colors).

How it connects
----------------
app.py calls inject_theme() once, immediately after st.set_page_config().
ui/components.py imports COLORS to keep badge/card colors consistent with
the CSS tokens below.
"""

import streamlit as st

COLORS = {
    "bg": "#0A0E14",
    "panel": "#11161F",
    "panel_alt": "#161C28",
    "border": "rgba(148, 163, 184, 0.08)",
    "border_strong": "rgba(148, 163, 184, 0.16)",
    "teal": "#00D9C0",
    "teal_soft": "rgba(0, 217, 192, 0.12)",
    "green": "#16C784",
    "green_soft": "rgba(22, 199, 132, 0.14)",
    "red": "#FF4D4D",
    "red_soft": "rgba(255, 77, 77, 0.14)",
    "amber": "#FFB020",
    "amber_soft": "rgba(255, 176, 32, 0.14)",
    "orange": "#FF8A3D",
    "orange_soft": "rgba(255, 138, 61, 0.14)",
    "text": "#E6EAF0",
    "muted": "#8A93A6",
    "faint": "#576075",
}

# Signal name -> (text color, soft background, glow) — single source of
# truth so ui/components.py and ui/tables.py never disagree on a badge color.
SIGNAL_STYLE = {
    "🔥 Strong Bullish": (COLORS["green"], COLORS["green_soft"], True),
    "✅ Bullish": (COLORS["green"], "rgba(22, 199, 132, 0.08)", False),
    "➖ Neutral": (COLORS["amber"], COLORS["amber_soft"], False),
    "⚠️ Bearish": (COLORS["orange"], COLORS["orange_soft"], False),
    "❌ Strong Bearish": (COLORS["red"], COLORS["red_soft"], True),
}


def render_html(content: str) -> None:
    """
    Two distinct Streamlit markdown quirks, both fixed here:

    1. CommonMark treats any line starting with 4+ spaces as an indented
       code block, so HTML/CSS written as nested, indented f-strings can
       render as literal text instead of being parsed as HTML.
    2. A documented Streamlit bug (github.com/streamlit/streamlit#586,
       #859): when a multi-line string passed to st.markdown with
       unsafe_allow_html=True contains a BLANK LINE, only the content
       *before* the first blank line is treated as raw HTML — everything
       after it falls back to plain markdown text. This is the actual
       cause of CSS rules appearing as visible text mid-page.

    Fix: strip leading/trailing whitespace from every line AND drop
    blank lines entirely before handing the string to st.markdown. Safe
    for HTML/CSS, which is whitespace-insensitive outside <pre>/<code>
    (none of our components use those).
    """
    lines = (line.strip() for line in content.split("\n"))
    cleaned = "\n".join(line for line in lines if line)
    st.markdown(cleaned, unsafe_allow_html=True)


def inject_theme() -> None:
    render_html(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
        <style>

        :root {
            --bg: #0A0E14;
            --panel: #11161F;
            --panel-alt: #161C28;
            --border: rgba(148, 163, 184, 0.08);
            --border-strong: rgba(148, 163, 184, 0.16);
            --teal: #00D9C0;
            --teal-soft: rgba(0, 217, 192, 0.12);
            --green: #16C784;
            --red: #FF4D4D;
            --amber: #FFB020;
            --orange: #FF8A3D;
            --text: #E6EAF0;
            --muted: #8A93A6;
            --faint: #576075;
            --font-display: 'Space Grotesk', sans-serif;
            --font-body: 'Inter', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        html, body, [class*="css"] { font-family: var(--font-body); }

        .stApp {
            background:
                radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,217,192,0.06), transparent),
                var(--bg);
            color: var(--text);
        }

        .block-container {
            padding-top: 0.75rem;
            padding-bottom: 4rem;
            max-width: 1200px;
        }

        /* ---------------- Scrollbars (desktop polish) ---------------- */
        ::-webkit-scrollbar { height: 6px; width: 6px; }
        ::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }

        /* ---------------- Headings ---------------- */
        h1, h2, h3 { font-family: var(--font-display) !important; letter-spacing: -0.01em; }

        /* ---------------- Sidebar ---------------- */
        section[data-testid="stSidebar"] {
            background: var(--panel);
            border-right: 1px solid var(--border);
        }

        /* ---------------- Buttons ---------------- */
        .stButton > button {
            background: linear-gradient(135deg, var(--teal), #00B8A3);
            color: #04211D;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            font-family: var(--font-body);
            padding: 0.55rem 1.1rem;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            box-shadow: 0 0 0 rgba(0,217,192,0);
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(0,217,192,0.25);
        }
        .stButton > button:active { transform: translateY(0); }

        .stDownloadButton > button {
            background: var(--panel-alt);
            color: var(--text);
            border: 1px solid var(--border-strong);
            border-radius: 10px;
            font-weight: 500;
        }
        .stDownloadButton > button:hover { border-color: var(--teal); color: var(--teal); }

        /* ---------------- Inputs ---------------- */
        .stTextInput input, .stDateInput input, .stSelectbox > div > div {
            background: var(--panel-alt) !important;
            border: 1px solid var(--border-strong) !important;
            border-radius: 10px !important;
            color: var(--text) !important;
        }

        .stSlider [data-baseweb="slider"] > div > div { background: var(--teal) !important; }

        /* ---------------- Tabs -> segmented pill nav ---------------- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 5px;
            position: sticky;
            top: 0;
            z-index: 999;
            overflow-x: auto;
            flex-wrap: nowrap;
            backdrop-filter: blur(10px);
        }
        .stTabs [data-baseweb="tab"] {
            height: 38px;
            border-radius: 10px;
            color: var(--muted);
            font-weight: 500;
            font-size: 0.85rem;
            white-space: nowrap;
            background: transparent;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--teal-soft), rgba(0,217,192,0.04)) !important;
            color: var(--teal) !important;
            font-weight: 600;
        }
        .stTabs [data-baseweb="tab-highlight"] { display: none; }
        .stTabs [data-baseweb="tab-border"] { display: none; }

        /* ---------------- Progress bar ---------------- */
        .stProgress > div > div > div { background: linear-gradient(90deg, var(--teal), var(--green)) !important; }

        /* ---------------- Metric (fallback native cards) ---------------- */
        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--border);
            padding: 14px 16px;
            border-radius: 14px;
        }

        /* ---------------- Alerts ---------------- */
        div[data-testid="stAlert"] {
            background: var(--panel) !important;
            border: 1px solid var(--border-strong) !important;
            border-radius: 12px !important;
        }

        /* ---------------- Custom component classes ---------------- */

        .mi-glass {
            background: linear-gradient(180deg, var(--panel), var(--panel-alt));
            border: 1px solid var(--border);
            border-radius: 16px;
        }

        .mi-fade-in { animation: miFadeIn 0.35s ease both; }
        @keyframes miFadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .mi-pulse-dot {
            width: 8px; height: 8px; border-radius: 50%;
            display: inline-block; margin-right: 6px;
            box-shadow: 0 0 0 0 rgba(22,199,132,0.6);
            animation: miPulse 2s infinite;
        }
        @keyframes miPulse {
            0%   { box-shadow: 0 0 0 0 rgba(22,199,132,0.55); }
            70%  { box-shadow: 0 0 0 7px rgba(22,199,132,0); }
            100% { box-shadow: 0 0 0 0 rgba(22,199,132,0); }
        }

        @media (prefers-reduced-motion: reduce) {
            .mi-fade-in, .mi-pulse-dot { animation: none !important; }
        }

        /* ---------------- Mobile tightening ---------------- */
        @media (max-width: 640px) {
            .block-container { padding-left: 0.6rem; padding-right: 0.6rem; }
            .stTabs [data-baseweb="tab"] { font-size: 0.78rem; padding: 0 10px; }
            h1 { font-size: 1.35rem !important; }
        }

        </style>
        """
    )
