"""Plotly chart builders for interactive analysis."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard.config import CONFIG
from dashboard.exceptions import ChartBuildError


PLOTLY_TEMPLATE = "plotly_white"


def sample_for_chart(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Limit chart rows to protect browser performance."""

    if len(dataframe) <= CONFIG.chart_sample_rows:
        return dataframe
    return dataframe.sample(CONFIG.chart_sample_rows, random_state=42)


def build_chart(
    dataframe: pd.DataFrame,
    chart_type: str,
    x_axis: str | None,
    y_axis: str | None,
    color: str | None,
) -> go.Figure:
    """Build a Plotly figure from user selections."""

    if dataframe.empty:
        raise ChartBuildError("برای ساخت نمودار، داده‌ای وجود ندارد.")

    chart_data = sample_for_chart(dataframe)
    try:
        if chart_type == "نمودار ستونی":
            figure = px.bar(chart_data, x=x_axis, y=y_axis, color=color, template=PLOTLY_TEMPLATE)
        elif chart_type == "نمودار خطی":
            figure = px.line(chart_data, x=x_axis, y=y_axis, color=color, template=PLOTLY_TEMPLATE)
        elif chart_type == "نمودار پراکندگی":
            figure = px.scatter(chart_data, x=x_axis, y=y_axis, color=color, template=PLOTLY_TEMPLATE)
        elif chart_type == "هیستوگرام":
            figure = px.histogram(chart_data, x=x_axis, color=color, template=PLOTLY_TEMPLATE)
        elif chart_type == "جعبه‌ای":
            figure = px.box(chart_data, x=x_axis, y=y_axis, color=color, template=PLOTLY_TEMPLATE)
        else:
            raise ChartBuildError("نوع نمودار انتخاب‌شده معتبر نیست.")
    except Exception as exc:
        raise ChartBuildError("نمودار با انتخاب‌های فعلی قابل ساخت نیست.") from exc

    figure.update_layout(
        font={"family": "Vazirmatn, Tahoma, Arial", "size": 13},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.72)",
        hovermode="x unified",
        margin={"l": 16, "r": 16, "t": 48, "b": 16},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    return figure


def correlation_heatmap(dataframe: pd.DataFrame) -> go.Figure | None:
    """Create a numeric correlation heatmap when possible."""

    numeric = dataframe.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return None

    corr = numeric.corr().round(3)
    figure = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        template=PLOTLY_TEMPLATE,
    )
    figure.update_layout(
        title="نقشه همبستگی ستون‌های عددی",
        font={"family": "Vazirmatn, Tahoma, Arial"},
        margin={"l": 16, "r": 16, "t": 56, "b": 16},
    )
    return figure
