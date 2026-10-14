"""Export helpers for processed data."""

from __future__ import annotations

import pandas as pd


def dataframe_to_csv(dataframe: pd.DataFrame) -> bytes:
    """Serialize dataframe to UTF-8 BOM CSV for Excel-friendly downloads."""

    return dataframe.to_csv(index=False).encode("utf-8-sig")
