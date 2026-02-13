"""Streamlit dashboard page layout and components."""

import logging

import pandas as pd
import streamlit as st

from power_cost.analysis.forecast import (
    compute_actual_consumption,
    forecast_summary,
)
from power_cost.analysis.stats import (
    compute_hourly_averages,
    compute_summary_stats,
)
from power_cost.ui.charts import (
    plot_cost_breakdown,
    plot_cpu_vs_gpu,
    plot_hourly_distribution,
    plot_power_over_time,
)

logger = logging.getLogger(__name__)


def render_sidebar(
    default_rate: float,
    default_efficiency: float,
) -> tuple[float, float]:
    """Render the sidebar with configurable parameters.

    Args:
        default_rate: Default electricity rate in USD/kWh.
        default_efficiency: Default PSU efficiency (0-1).

    Returns:
        Tuple of (rate, psu_efficiency) as set by the user.
    """
    st.sidebar.header("Settings")
    rate = st.sidebar.number_input(
        "Electricity Rate (USD/kWh)",
        min_value=0.01,
        max_value=1.00,
        value=default_rate,
        step=0.01,
        format="%.4f",
    )
    efficiency = st.sidebar.slider(
        "PSU Efficiency (%)",
        min_value=50,
        max_value=100,
        value=int(default_efficiency * 100),
        step=1,
    )
    return float(rate), efficiency / 100.0


def render_metrics(forecast: dict[str, float]) -> None:
    """Display key metrics as Streamlit metric cards.

    Args:
        forecast: Dictionary returned by ``forecast_summary``.
    """
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Total Watts", f"{forecast['avg_total_watts']:.1f} W")
    col2.metric("Wall Draw", f"{forecast['wall_watts']:.1f} W")
    col3.metric("Monthly kWh", f"{forecast['monthly_kwh']:.1f}")
    col4.metric("Monthly Cost", f"${forecast['monthly_cost_usd']:.2f}")


def render_dashboard(df: pd.DataFrame) -> None:
    """Render the full dashboard.

    Args:
        df: Validated power log DataFrame.
    """
    from power_cost.config import ELECTRICITY_RATE_PER_KWH, PSU_EFFICIENCY

    st.title("Power Cost Dashboard")
    st.caption("Laptop power consumption analysis and 24/7 cost forecast")

    # -- Sidebar --
    rate, psu_eff = render_sidebar(ELECTRICITY_RATE_PER_KWH, PSU_EFFICIENCY)

    # -- Forecast --
    forecast = forecast_summary(df, rate=rate, psu_efficiency=psu_eff)
    render_metrics(forecast)

    st.divider()

    # -- Actual consumption to date --
    actual = compute_actual_consumption(df, rate=rate, psu_efficiency=psu_eff)
    start_dt = actual["start"]
    end_dt = actual["end"]
    num_days = actual["num_days"]
    date_range = (
        f"{start_dt:%b %d} - {end_dt:%b %d}"  # type: ignore[str-format]
        if num_days > 1
        else f"{start_dt:%b %d}"  # type: ignore[str-format]
    )

    st.subheader(f"Actual Consumption ({date_range}, {num_days} day(s))")
    act_c1, act_c2, act_c3 = st.columns(3)
    act_c1.metric(
        "Period kWh",
        f"{actual['actual_kwh']:.4f}",
    )
    act_c2.metric(
        "Period Cost",
        f"${actual['actual_cost_usd']:.4f}",
    )
    act_c3.metric(
        "Monitoring Hours",
        f"{actual['total_hours']:.1f} h",
    )

    daily_breakdown = actual["daily_breakdown"]
    if isinstance(daily_breakdown, pd.DataFrame) and not daily_breakdown.empty:
        display_df = daily_breakdown.copy()
        display_df.index = display_df.index.strftime("%b %d")  # type: ignore[attr-defined]
        display_df.columns = [
            "Daily kWh",
            "Daily Cost (USD)",
            "Cumulative kWh",
            "Cumulative Cost (USD)",
        ]
        st.dataframe(display_df.style.format("{:.4f}"), width="stretch")

    st.divider()

    # -- Summary statistics --
    stats = compute_summary_stats(df)
    with st.expander("Summary Statistics", expanded=False):
        stat_cols = st.columns(3)
        for idx, (label, data) in enumerate(stats.items()):
            with stat_cols[idx]:
                st.subheader(label.upper())
                for metric_name, value in data.items():
                    st.text(f"{metric_name}: {value:.2f} W")

    # -- Charts --
    st.subheader("Power Over Time")
    st.plotly_chart(plot_power_over_time(df), width="stretch")

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("CPU vs GPU")
        st.plotly_chart(plot_cpu_vs_gpu(df), width="stretch")

    with col_right:
        st.subheader("Hourly Distribution")
        hourly = compute_hourly_averages(df)
        if not hourly.empty:
            st.plotly_chart(
                plot_hourly_distribution(hourly), width="stretch"
            )
        else:
            st.info("Not enough data for hourly distribution.")

    st.subheader("Cost Forecast")
    st.plotly_chart(plot_cost_breakdown(forecast), width="stretch")

    # -- Raw data --
    with st.expander("Raw Data", expanded=False):
        st.dataframe(df, width="stretch")

    logger.info("Dashboard rendered with %d data points", len(df))
