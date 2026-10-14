"""Reusable Streamlit UI components."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


def load_css(css_file: Path) -> None:
    """Inject the RTL design system stylesheet."""

    if css_file.exists():
        stylesheet = css_file.read_text(encoding="utf-8")
        st.markdown(f"<style>{stylesheet}</style>", unsafe_allow_html=True)


def render_header(title: str, subtitle: str) -> None:
    """Render the main gradient header."""

    st.markdown(
        f"""
        <section class="hero" dir="rtl" lang="fa">
            <div>
                <span class="eyebrow">فضای تحلیل داده</span>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(metrics: dict[str, float | int]) -> None:
    """Render high-level KPI cards."""

    labels = {
        "rows": "تعداد ردیف",
        "columns": "تعداد ستون",
        "missing_cells": "سلول خالی",
        "duplicate_rows": "ردیف تکراری",
        "completeness": "درصد تکمیل داده",
    }
    values = {
        "rows": _to_persian_digits(f"{metrics['rows']:,}"),
        "columns": _to_persian_digits(f"{metrics['columns']:,}"),
        "missing_cells": _to_persian_digits(f"{metrics['missing_cells']:,}"),
        "duplicate_rows": _to_persian_digits(f"{metrics['duplicate_rows']:,}"),
        "completeness": f"{_to_persian_digits(str(metrics['completeness']))}٪",
    }

    cards = "".join(
        f'<div class="kpi-card"><span>{labels[key]}</span>'
        f"<strong>{values[key]}</strong></div>"
        for key in labels
    )
    st.markdown(
        (
            '<section class="kpi-grid" dir="rtl" aria-label="شاخص‌های داده">'
            f"{cards}</section>"
        ),
        unsafe_allow_html=True,
    )


def _to_persian_digits(value: str) -> str:
    """Format numeric labels with Persian digits and separators."""

    translation = str.maketrans("0123456789,.", "۰۱۲۳۴۵۶۷۸۹٬٫")
    return value.translate(translation)


def render_empty_state() -> None:
    """Show guidance before a file is uploaded."""

    st.markdown(
        """
        <div class="empty-state" dir="rtl" lang="fa">
            <h2>برای شروع، یک فایل داده بارگذاری کنید</h2>
            <p>فایل CSV یا Excel خود را از سایدبار انتخاب کنید تا پروفایل داده، فیلترها و نمودارهای تعاملی فعال شوند.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dataframe(dataframe: pd.DataFrame, rows: int) -> None:
    """Render a responsive dataframe preview."""

    st.dataframe(
        dataframe.head(rows),
        use_container_width=True,
        hide_index=True,
    )


def show_success(message: str) -> None:
    """Render a consistent success notification."""

    st.success(message)


def show_error(message: str) -> None:
    """Render a consistent Persian error notification."""

    st.error(message)
