"""Plotly chart builders for power consumption visualisation."""

import logging

import pandas as pd
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


def plot_power_over_time(df: pd.DataFrame) -> go.Figure:
    """Create a time-series line chart of CPU, GPU, and total wattage.

    Args:
        df: DataFrame with DatetimeIndex and watt columns.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["CPU_Watts"],
            name="CPU",
            mode="lines",
            line={"color": "#636EFA"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["GPU_Watts"],
            name="GPU",
            mode="lines",
            line={"color": "#EF553B"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Total_Watts"],
            name="Total",
            mode="lines",
            line={"color": "#00CC96", "dash": "dash"},
        )
    )
    fig.update_layout(
        title="Power Consumption Over Time",
        xaxis_title="Time",
        yaxis_title="Watts",
        template="plotly_dark",
        hovermode="x unified",
    )
    logger.debug("Built power-over-time chart with %d points", len(df))
    return fig


def plot_cpu_vs_gpu(df: pd.DataFrame) -> go.Figure:
    """Create a scatter plot comparing CPU vs GPU wattage.

    Args:
        df: DataFrame with ``CPU_Watts`` and ``GPU_Watts`` columns.

    Returns:
        Plotly Figure.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["CPU_Watts"],
            y=df["GPU_Watts"],
            mode="markers",
            marker={"color": "#AB63FA", "opacity": 0.6},
            name="Reading",
        )
    )
    fig.update_layout(
        title="CPU vs GPU Power Draw",
        xaxis_title="CPU Watts",
        yaxis_title="GPU Watts",
        template="plotly_dark",
    )
    return fig


def plot_hourly_distribution(hourly_df: pd.DataFrame) -> go.Figure:
    """Create a bar chart of average total wattage by hour of day.

    Args:
        hourly_df: DataFrame with DatetimeIndex (hourly resolution)
            and a ``Total_Watts`` column.

    Returns:
        Plotly Figure.
    """
    by_hour = hourly_df.copy()
    by_hour["hour"] = by_hour.index.hour  # type: ignore[union-attr]
    grouped = by_hour.groupby("hour")["Total_Watts"].mean()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=grouped.index,
            y=grouped.values,
            marker_color="#FFA15A",
            name="Avg Total Watts",
        )
    )
    fig.update_layout(
        title="Average Power Draw by Hour of Day",
        xaxis_title="Hour",
        yaxis_title="Watts",
        template="plotly_dark",
    )
    return fig


def plot_cost_breakdown(forecast: dict[str, float]) -> go.Figure:
    """Create a summary gauge / indicator for monthly cost.

    Args:
        forecast: Dictionary returned by ``forecast_summary``.

    Returns:
        Plotly Figure with indicator traces.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=forecast["monthly_cost_usd"],
            number={"prefix": "$", "valueformat": ".2f"},
            title={"text": "Estimated Monthly Cost"},
            domain={"x": [0, 0.5], "y": [0, 1]},
        )
    )
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=forecast["monthly_kwh"],
            number={"suffix": " kWh", "valueformat": ".1f"},
            title={"text": "Estimated Monthly Consumption"},
            domain={"x": [0.5, 1], "y": [0, 1]},
        )
    )
    fig.update_layout(template="plotly_dark")
    return fig
