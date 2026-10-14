"""Persian Streamlit dashboard for data analysis and chart creation."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from dashboard.charts import build_chart, correlation_heatmap
from dashboard.config import CONFIG
from dashboard.data_loader import load_dataframe
from dashboard.data_profile import (
    clean_dataframe,
    column_profile,
    describe_numeric,
    infer_datetime_columns,
    quality_metrics,
    split_columns,
)
from dashboard.exceptions import ChartBuildError, DashboardError
from dashboard.exporters import dataframe_to_csv
from dashboard.filters import render_filters
from dashboard.logging_config import configure_logging
from dashboard.ui_components import (
    load_css,
    render_dataframe,
    render_empty_state,
    render_header,
    render_kpis,
    show_error,
    show_success,
)


logger = configure_logging()


@st.cache_data(show_spinner="در حال خواندن فایل...")
def cached_load(file_bytes: bytes, filename: str, size: int) -> pd.DataFrame:
    """Load uploaded bytes through the validated data loader."""

    from io import BytesIO

    return load_dataframe(BytesIO(file_bytes), filename=filename, size=size)


def configure_page() -> None:
    """Apply Streamlit page settings."""

    st.set_page_config(
        page_title=CONFIG.app_name,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="auto",
    )
    load_css(CONFIG.css_file)


def sidebar_controls() -> tuple[bytes | None, str | None, int | None, bool, str, int]:
    """Render sidebar controls and return selected options."""

    st.sidebar.title("ناوبری داشبورد")
    st.sidebar.caption("فایل خود را بارگذاری کنید و سپس تنظیمات تحلیل را انتخاب کنید.")

    uploaded_file = st.sidebar.file_uploader(
        "بارگذاری فایل",
        type=list(CONFIG.allowed_extensions),
        help=f"حداکثر حجم فایل: {CONFIG.max_file_size_mb} مگابایت",
    )
    st.sidebar.caption(
        "فایل CSV یا Excel را اینجا رها کنید یا با دکمه‌ی «بارگذاری فایل» برگزینید. "
        f"حداکثر حجم: {CONFIG.max_file_size_mb} مگابایت."
    )

    st.sidebar.divider()
    st.sidebar.subheader("پاک‌سازی داده")
    remove_duplicates = st.sidebar.checkbox("حذف ردیف‌های تکراری", value=True)
    missing_strategy = st.sidebar.selectbox(
        "مدیریت مقادیر خالی",
        options=[
            "بدون تغییر",
            "حذف ردیف‌های دارای مقدار خالی",
            "جایگزینی عددی با میانه و متنی با مقدار پرتکرار",
            "جایگزینی با صفر برای ستون‌های عددی",
        ],
    )
    preview_rows = st.sidebar.number_input(
        "تعداد ردیف پیش‌نمایش",
        min_value=10,
        max_value=10_000,
        value=CONFIG.preview_rows,
        step=100,
    )

    if uploaded_file is None:
        return None, None, None, remove_duplicates, missing_strategy, int(preview_rows)

    return (
        uploaded_file.getvalue(),
        uploaded_file.name,
        uploaded_file.size,
        remove_duplicates,
        missing_strategy,
        int(preview_rows),
    )


def render_chart_builder(dataframe: pd.DataFrame) -> None:
    """Render chart controls and the resulting interactive chart."""

    st.subheader("نمودارساز تعاملی")
    column_types = split_columns(dataframe)
    all_columns = dataframe.columns.tolist()
    numeric_columns = column_types["numeric"]

    chart_type = st.selectbox(
        "نوع نمودار",
        ["نمودار ستونی", "نمودار خطی", "نمودار پراکندگی", "هیستوگرام", "جعبه‌ای"],
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        x_axis = st.selectbox("محور افقی", all_columns)
    with col2:
        y_options = [""] + numeric_columns
        y_axis = st.selectbox("محور عمودی", y_options)
    with col3:
        color_options = [""] + all_columns
        color = st.selectbox("رنگ‌بندی", color_options)

    try:
        figure = build_chart(
            dataframe=dataframe,
            chart_type=chart_type,
            x_axis=x_axis or None,
            y_axis=y_axis or None,
            color=color or None,
        )
        st.plotly_chart(figure, use_container_width=True)
    except ChartBuildError as exc:
        show_error(str(exc))


def render_dashboard(dataframe: pd.DataFrame, preview_rows: int) -> None:
    """Render all analysis tabs for a prepared dataframe."""

    metrics = quality_metrics(dataframe)
    render_kpis(metrics)

    tab_data, tab_profile, tab_charts, tab_export = st.tabs(
        ["نمای داده", "کیفیت و آمار", "نمودارها", "خروجی"]
    )

    with tab_data:
        filtered = render_filters(dataframe)
        st.caption(f"تعداد ردیف پس از فیلتر: {len(filtered):,}")
        render_dataframe(filtered, preview_rows)
        st.session_state["filtered_dataframe"] = filtered

    with tab_profile:
        st.subheader("پروفایل ستون‌ها")
        st.dataframe(column_profile(dataframe), use_container_width=True, hide_index=True)

        stats = describe_numeric(dataframe)
        if stats.empty:
            st.info("ستون عددی برای تحلیل آماری پیدا نشد.")
        else:
            st.subheader("آمار توصیفی")
            st.dataframe(stats, use_container_width=True)

        heatmap = correlation_heatmap(dataframe)
        if heatmap is not None:
            st.plotly_chart(heatmap, use_container_width=True)

    with tab_charts:
        filtered = st.session_state.get("filtered_dataframe", dataframe)
        if filtered.empty:
            st.info("با فیلترهای فعلی داده‌ای برای نمودار وجود ندارد.")
        else:
            render_chart_builder(filtered)

    with tab_export:
        filtered = st.session_state.get("filtered_dataframe", dataframe)
        st.subheader("دانلود داده پردازش‌شده")
        st.write("خروجی شامل داده‌ی پاک‌سازی‌شده و فیلترهای اعمال‌شده است.")
        st.download_button(
            "دانلود CSV",
            data=dataframe_to_csv(filtered),
            file_name="processed_data.csv",
            mime="text/csv",
        )


def main() -> None:
    """Application entry point."""

    configure_page()
    render_header(
        CONFIG.app_name,
        "فایل‌های CSV و Excel را تحلیل کنید، کیفیت داده را ببینید، فیلتر بسازید و نمودارهای مدیریتی تعاملی تولید کنید.",
    )

    (
        file_bytes,
        filename,
        size,
        remove_duplicates,
        missing_strategy,
        preview_rows,
    ) = sidebar_controls()
    if file_bytes is None or filename is None or size is None:
        render_empty_state()
        return

    try:
        dataframe = cached_load(file_bytes, filename, size)
        dataframe = infer_datetime_columns(dataframe)
        dataframe = clean_dataframe(
            dataframe,
            remove_duplicates=remove_duplicates,
            missing_strategy=missing_strategy,
        )
        logger.info(
            "file_loaded",
            extra={"rows": len(dataframe), "columns": len(dataframe.columns)},
        )
        show_success("فایل با موفقیت بارگذاری و آماده تحلیل شد.")
        render_dashboard(dataframe, preview_rows)
    except DashboardError as exc:
        logger.warning("user_facing_error", extra={"error": str(exc)})
        show_error(str(exc))
    except Exception:  # pragma: no cover - final safety net for UI runtime.
        logger.exception("unexpected_error")
        show_error("خطای غیرمنتظره‌ای رخ داد. لطفاً فایل یا تنظیمات را بررسی کنید.")


if __name__ == "__main__":
    main()
