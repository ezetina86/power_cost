"""Descriptive statistics for power consumption data."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def compute_summary_stats(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    """Compute descriptive statistics for CPU, GPU, and total power.

    Args:
        df: DataFrame with ``CPU_Watts``, ``GPU_Watts``, and ``Total_Watts``
            columns.

    Returns:
        Nested dict keyed by metric name (``cpu``, ``gpu``, ``total``), each
        containing ``mean``, ``median``, ``min``, ``max``, and ``std``.
    """
    stats: dict[str, dict[str, float]] = {}
    for label, col in [
        ("cpu", "CPU_Watts"),
        ("gpu", "GPU_Watts"),
        ("total", "Total_Watts"),
    ]:
        series = df[col]
        stats[label] = {
            "mean": float(series.mean()),
            "median": float(series.median()),
            "min": float(series.min()),
            "max": float(series.max()),
            "std": float(series.std()),
        }

    logger.info("Computed summary statistics for %d readings", len(df))
    return stats


def compute_hourly_averages(df: pd.DataFrame) -> pd.DataFrame:
    """Resample power data into hourly averages.

    Args:
        df: DataFrame with a DatetimeIndex and watt columns.

    Returns:
        DataFrame resampled to 1-hour frequency with mean values.
    """
    hourly = df.resample("1h").mean()
    hourly = hourly.dropna()
    logger.debug("Resampled to %d hourly buckets", len(hourly))
    return hourly


def compute_daily_averages(df: pd.DataFrame) -> pd.DataFrame:
    """Resample power data into daily averages.

    Args:
        df: DataFrame with a DatetimeIndex and watt columns.

    Returns:
        DataFrame resampled to 1-day frequency with mean values.
    """
    daily = df.resample("1D").mean()
    daily = daily.dropna()
    logger.debug("Resampled to %d daily buckets", len(daily))
    return daily
