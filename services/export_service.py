"""
services/export_service.py

Purpose
-------
All Excel-generation logic in one place. The original app.py's
create_excel() function, plus named wrappers so call sites in app.py read
clearly (export_india(df) instead of a bare create_excel(df) repeated
three times).

Inputs
------
df: pandas.DataFrame

Outputs
-------
bytes - an .xlsx file ready for st.download_button's `data` argument.

How it connects
----------------
ui/tables.py (or app.py) calls export_india/export_usa/export_scanner
right before rendering each st.download_button.
"""

from io import BytesIO

import pandas as pd

from utils.helpers import get_logger

logger = get_logger(__name__)


def create_excel(df: pd.DataFrame) -> bytes:
    """Serialize a DataFrame to .xlsx bytes via openpyxl. Identical to the original app."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()


def export_india(df: pd.DataFrame) -> bytes:
    return create_excel(df)


def export_usa(df: pd.DataFrame) -> bytes:
    return create_excel(df)


def export_scanner(df: pd.DataFrame) -> bytes:
    return create_excel(df)
