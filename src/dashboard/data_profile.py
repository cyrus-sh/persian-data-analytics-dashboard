"""Data profiling, cleaning, and summary helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd


def split_columns(dataframe: pd.DataFrame) -> dict[str, list[str]]:
    """Group columns by analytical type."""

    numeric = dataframe.select_dtypes(include="number").columns.tolist()
    datetime = dataframe.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    categorical = [
        column
        for column in dataframe.columns
        if column not in numeric and column not in datetime
    ]
    return {"numeric": numeric, "datetime": datetime, "categorical": categorical}


def infer_datetime_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Convert likely date columns while avoiding destructive type changes."""

    converted = dataframe.copy()
    for column in converted.columns:
        if pd.api.types.is_object_dtype(converted[column]) or pd.api.types.is_string_dtype(
            converted[column].dtype
        ):
            sample = converted[column].dropna().astype(str).head(100)
            if sample.empty:
                continue
            parsed = pd.to_datetime(sample, errors="coerce")
            if parsed.notna().mean() >= 0.8:
                converted[column] = pd.to_datetime(converted[column], errors="coerce")
    return converted


def quality_metrics(dataframe: pd.DataFrame) -> dict[str, float | int]:
    """Calculate high-level data quality metrics."""

    total_cells = int(dataframe.shape[0] * dataframe.shape[1])
    missing_cells = int(dataframe.isna().sum().sum())
    duplicate_rows = int(dataframe.duplicated().sum())
    completeness = 100.0 if total_cells == 0 else (1 - missing_cells / total_cells) * 100
    return {
        "rows": int(dataframe.shape[0]),
        "columns": int(dataframe.shape[1]),
        "missing_cells": missing_cells,
        "duplicate_rows": duplicate_rows,
        "completeness": round(completeness, 2),
    }


def column_profile(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Create a compact per-column profile table."""

    profile = pd.DataFrame(
        {
            "ستون": dataframe.columns,
            "نوع داده": [str(dtype) for dtype in dataframe.dtypes],
            "مقادیر خالی": dataframe.isna().sum().to_numpy(),
            "درصد خالی": (dataframe.isna().mean() * 100).round(2).to_numpy(),
            "مقادیر یکتا": dataframe.nunique(dropna=True).to_numpy(),
        }
    )
    return profile


def clean_dataframe(
    dataframe: pd.DataFrame,
    *,
    remove_duplicates: bool,
    missing_strategy: str,
) -> pd.DataFrame:
    """Apply non-destructive cleaning operations selected by the user."""

    cleaned = dataframe.copy()
    if remove_duplicates:
        cleaned = cleaned.drop_duplicates()

    if missing_strategy == "حذف ردیف‌های دارای مقدار خالی":
        cleaned = cleaned.dropna()
    elif missing_strategy == "جایگزینی عددی با میانه و متنی با مقدار پرتکرار":
        cleaned = _fill_missing_with_smart_defaults(cleaned)
    elif missing_strategy == "جایگزینی با صفر برای ستون‌های عددی":
        numeric_cols = cleaned.select_dtypes(include="number").columns
        cleaned.loc[:, numeric_cols] = cleaned[numeric_cols].fillna(0)

    return cleaned.convert_dtypes()


def _fill_missing_with_smart_defaults(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values using median for numeric and mode for other columns."""

    filled = dataframe.copy()
    for column in filled.columns:
        series = filled[column]
        if pd.api.types.is_numeric_dtype(series):
            median = series.median()
            filled[column] = series.fillna(0 if pd.isna(median) else median)
            continue

        mode = series.mode(dropna=True)
        fallback = "نامشخص" if mode.empty else mode.iloc[0]
        filled[column] = series.fillna(fallback)
    return filled


def describe_numeric(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return Persian-labeled descriptive statistics for numeric columns."""

    numeric = dataframe.select_dtypes(include="number")
    if numeric.empty:
        return pd.DataFrame()

    stats = numeric.describe().T
    stats = stats.rename(
        columns={
            "count": "تعداد",
            "mean": "میانگین",
            "std": "انحراف معیار",
            "min": "کمینه",
            "25%": "چارک اول",
            "50%": "میانه",
            "75%": "چارک سوم",
            "max": "بیشینه",
        }
    )
    return stats.replace([np.inf, -np.inf], np.nan).round(3)
