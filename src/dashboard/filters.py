"""Reusable dataframe filters driven by Streamlit widgets."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_filters(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Render type-aware filters and return the filtered dataframe."""

    filtered = dataframe.copy()
    with st.expander("فیلترهای داده", expanded=True):
        for column in dataframe.columns:
            series = dataframe[column]
            if pd.api.types.is_numeric_dtype(series):
                filtered = _filter_numeric(filtered, column, series)
            elif pd.api.types.is_datetime64_any_dtype(series):
                filtered = _filter_datetime(filtered, column, series)
            else:
                filtered = _filter_categorical(filtered, column, series)
    return filtered


def _filter_numeric(
    filtered: pd.DataFrame,
    column: str,
    series: pd.Series,
) -> pd.DataFrame:
    values = series.dropna()
    if values.empty:
        return filtered

    minimum = float(values.min())
    maximum = float(values.max())
    if minimum == maximum:
        return filtered

    selected = st.slider(
        f"بازه {column}",
        min_value=minimum,
        max_value=maximum,
        value=(minimum, maximum),
    )
    return filtered[filtered[column].between(selected[0], selected[1]) | filtered[column].isna()]


def _filter_datetime(
    filtered: pd.DataFrame,
    column: str,
    series: pd.Series,
) -> pd.DataFrame:
    values = series.dropna()
    if values.empty:
        return filtered

    start, end = st.date_input(
        f"بازه تاریخی {column}",
        value=(values.min().date(), values.max().date()),
    )
    if not start or not end:
        return filtered

    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    return filtered[(filtered[column] >= start_ts) & (filtered[column] <= end_ts)]


def _filter_categorical(
    filtered: pd.DataFrame,
    column: str,
    series: pd.Series,
) -> pd.DataFrame:
    unique_values = series.dropna().astype(str).sort_values().unique().tolist()
    if not unique_values or len(unique_values) > 200:
        return filtered

    selected = st.multiselect(
        f"انتخاب از {column}",
        options=unique_values,
        default=unique_values,
        help="برای ستون‌های با تعداد مقدار یکتای زیاد، فیلتر خودکار نمایش داده نمی‌شود.",
    )
    if not selected:
        return filtered.iloc[0:0]
    return filtered[filtered[column].astype(str).isin(selected) | filtered[column].isna()]
