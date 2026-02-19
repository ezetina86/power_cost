"""Cost forecasting logic based on power consumption data."""

import logging

import pandas as pd

from power_cost.config import (
    ELECTRICITY_RATE_PER_KWH,
    HOURS_PER_MONTH,
    PSU_EFFICIENCY,
)

logger = logging.getLogger(__name__)


def watts_to_kwh(watts: float, hours: float) -> float:
    """Convert a power draw to energy consumed.

    Args:
        watts: Average power draw in watts.
        hours: Duration in hours.

    Returns:
        Energy consumed in kilowatt-hours.
    """
    return (watts / 1000.0) * hours


def estimate_monthly_kwh(
    avg_watts: float,
    hours: float = HOURS_PER_MONTH,
    psu_efficiency: float = PSU_EFFICIENCY,
) -> float:
    """Project average watts to monthly energy consumption at the wall.

    The wall consumption accounts for PSU efficiency losses.

    Args:
        avg_watts: Average component power draw in watts.
        hours: Hours per month (default from config).
        psu_efficiency: PSU efficiency factor (0-1).

    Returns:
        Estimated monthly wall consumption in kWh.
    """
    wall_watts = avg_watts / psu_efficiency
    return watts_to_kwh(wall_watts, hours)


def estimate_monthly_cost(
    monthly_kwh: float,
    rate: float = ELECTRICITY_RATE_PER_KWH,
) -> float:
    """Calculate the monthly electricity cost.

    Args:
        monthly_kwh: Monthly energy consumption in kWh.
        rate: Electricity rate in USD per kWh.

    Returns:
        Estimated monthly cost in USD.
    """
    return monthly_kwh * rate


def forecast_summary(
    df: pd.DataFrame,
    rate: float = ELECTRICITY_RATE_PER_KWH,
    psu_efficiency: float = PSU_EFFICIENCY,
) -> dict[str, float]:
    """Build a complete cost forecast from power readings.

    Args:
        df: DataFrame containing a ``Total_Watts`` column.
        rate: Electricity rate in USD per kWh.
        psu_efficiency: PSU efficiency factor (0-1).

    Returns:
        Dictionary with forecasting results including average watts,
        monthly kWh, and monthly cost.
    """
    avg_watts = float(df["Total_Watts"].mean())
    monthly_kwh = estimate_monthly_kwh(avg_watts, psu_efficiency=psu_efficiency)
    monthly_cost = estimate_monthly_cost(monthly_kwh, rate=rate)

    summary = {
        "avg_total_watts": avg_watts,
        "avg_cpu_watts": float(df["CPU_Watts"].mean()),
        "avg_gpu_watts": float(df["GPU_Watts"].mean()),
        "wall_watts": avg_watts / psu_efficiency,
        "monthly_kwh": monthly_kwh,
        "monthly_cost_usd": monthly_cost,
        "daily_kwh": monthly_kwh / 30.0,
        "daily_cost_usd": monthly_cost / 30.0,
        "rate_per_kwh": rate,
        "psu_efficiency": psu_efficiency,
    }

    logger.info(
        "Forecast: %.1f W avg -> %.1f kWh/month -> $%.2f/month",
        avg_watts,
        monthly_kwh,
        monthly_cost,
    )
    return summary


def compute_actual_consumption(
    df: pd.DataFrame,
    rate: float = ELECTRICITY_RATE_PER_KWH,
    psu_efficiency: float = PSU_EFFICIENCY,
) -> dict[str, object]:
    """Compute the actual energy consumed and cost over the data period.

    Uses the first and last timestamps to determine the monitoring
    window, then sums per-minute readings to get real consumption.

    Args:
        df: DataFrame with DatetimeIndex and ``Total_Watts`` column.
        rate: Electricity rate in USD per kWh.
        psu_efficiency: PSU efficiency factor (0-1).

    Returns:
        Dictionary with period info, actual kWh, actual cost, and
        day-by-day breakdown.
    """
    start = df.index.min()
    end = df.index.max()
    duration = end - start
    total_hours = duration.total_seconds() / 3600.0
    num_days = max(duration.days, 1)

    # Each row represents ~1 minute of sampling.  Convert each reading
    # to kWh for that minute (1/60 of an hour) at the wall.
    minutes_factor = 1.0 / 60.0

    # Optimized: Sum first then multiply to reduce operations
    kwh_factor = (1.0 / psu_efficiency) * minutes_factor / 1000.0
    actual_kwh = float(df["Total_Watts"].sum() * kwh_factor)
    actual_cost = actual_kwh * rate

    # Day-by-day breakdown.
    # Optimized: Removed unnecessary df copy and temporary columns
    daily_cost = (
        (df["Total_Watts"] * kwh_factor)
        .resample("1D")
        .sum()
        .rename("daily_kwh")
        .to_frame()
    )
    daily_cost["daily_cost_usd"] = daily_cost["daily_kwh"] * rate
    daily_cost["cumulative_kwh"] = daily_cost["daily_kwh"].cumsum()
    daily_cost["cumulative_cost_usd"] = daily_cost["cumulative_kwh"] * rate

    result: dict[str, object] = {
        "start": start,
        "end": end,
        "total_hours": total_hours,
        "num_days": num_days,
        "actual_kwh": actual_kwh,
        "actual_cost_usd": actual_cost,
        "rate_per_kwh": rate,
        "daily_breakdown": daily_cost,
    }

    logger.info(
        "Actual: %.3f kWh over %.1f hours (%d day(s)) -> $%.4f",
        actual_kwh,
        total_hours,
        num_days,
        actual_cost,
    )
    return result
