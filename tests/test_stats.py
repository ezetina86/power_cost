"""Tests for the power_cost.analysis.stats module."""

import pandas as pd
import pytest

from power_cost.analysis.stats import (
    compute_daily_averages,
    compute_hourly_averages,
    compute_summary_stats,
)


class TestComputeSummaryStats:
    """Tests for compute_summary_stats."""

    def test_returns_all_keys(self, sample_df_raw):
        """Verify the result contains cpu, gpu, and total keys."""
        stats = compute_summary_stats(sample_df_raw)
        assert set(stats.keys()) == {"cpu", "gpu", "total"}

    def test_stat_keys(self, sample_df_raw):
        """Verify each metric has mean, median, min, max, std."""
        stats = compute_summary_stats(sample_df_raw)
        expected_keys = {"mean", "median", "min", "max", "std"}
        for label in ("cpu", "gpu", "total"):
            assert set(stats[label].keys()) == expected_keys

    def test_mean_values(self, sample_df_raw):
        """Verify mean is computed correctly."""
        stats = compute_summary_stats(sample_df_raw)
        assert stats["cpu"]["mean"] == pytest.approx(4.1, abs=0.01)
        assert stats["gpu"]["mean"] == pytest.approx(19.1, abs=0.01)
        assert stats["total"]["mean"] == pytest.approx(23.2, abs=0.01)

    def test_min_max(self, sample_df_raw):
        """Verify min and max are computed correctly."""
        stats = compute_summary_stats(sample_df_raw)
        assert stats["cpu"]["min"] == pytest.approx(3.5)
        assert stats["cpu"]["max"] == pytest.approx(5.0)


class TestComputeHourlyAverages:
    """Tests for compute_hourly_averages."""

    def test_returns_dataframe(self, sample_df):
        """Verify the result is a DataFrame."""
        result = compute_hourly_averages(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_fewer_rows_than_input(self, sample_df):
        """Hourly resampling should produce fewer rows than minute data."""
        result = compute_hourly_averages(sample_df)
        assert len(result) <= len(sample_df)


class TestComputeDailyAverages:
    """Tests for compute_daily_averages."""

    def test_returns_dataframe(self, sample_df):
        """Verify the result is a DataFrame."""
        result = compute_daily_averages(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_single_day_data(self, sample_df):
        """With single-day data, daily average should return one row."""
        result = compute_daily_averages(sample_df)
        assert len(result) == 1
