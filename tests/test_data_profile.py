from __future__ import annotations

import pandas as pd

from dashboard.data_profile import clean_dataframe, quality_metrics, split_columns


def test_quality_metrics_counts_missing_and_duplicates() -> None:
    dataframe = pd.DataFrame({"city": ["تهران", "تهران", None], "sales": [10, 10, None]})

    metrics = quality_metrics(dataframe)

    assert metrics["rows"] == 3
    assert metrics["columns"] == 2
    assert metrics["missing_cells"] == 2
    assert metrics["duplicate_rows"] == 1


def test_clean_dataframe_removes_duplicates() -> None:
    dataframe = pd.DataFrame({"city": ["تهران", "تهران"], "sales": [10, 10]})

    cleaned = clean_dataframe(
        dataframe,
        remove_duplicates=True,
        missing_strategy="بدون تغییر",
    )

    assert len(cleaned) == 1


def test_split_columns_detects_numeric() -> None:
    dataframe = pd.DataFrame({"city": ["تهران"], "sales": [10]})

    result = split_columns(dataframe)

    assert result["numeric"] == ["sales"]
    assert result["categorical"] == ["city"]
