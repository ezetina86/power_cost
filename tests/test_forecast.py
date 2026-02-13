"""Tests for the power_cost.analysis.forecast module."""

import pytest

from power_cost.analysis.forecast import (
    compute_actual_consumption,
    estimate_monthly_cost,
    estimate_monthly_kwh,
    forecast_summary,
    watts_to_kwh,
)


class TestWattsToKwh:
    """Tests for watts_to_kwh."""

    def test_basic_conversion(self):
        """1000 W for 1 hour should equal 1 kWh."""
        assert watts_to_kwh(1000.0, 1.0) == pytest.approx(1.0)

    def test_fractional(self):
        """500 W for 2 hours should equal 1 kWh."""
        assert watts_to_kwh(500.0, 2.0) == pytest.approx(1.0)

    def test_zero_watts(self):
        """Zero watts should produce zero kWh."""
        assert watts_to_kwh(0.0, 24.0) == pytest.approx(0.0)

    def test_zero_hours(self):
        """Zero hours should produce zero kWh."""
        assert watts_to_kwh(100.0, 0.0) == pytest.approx(0.0)


class TestEstimateMonthlyKwh:
    """Tests for estimate_monthly_kwh."""

    def test_known_value(self):
        """25 W avg at 100% efficiency over 720h should be 18 kWh."""
        result = estimate_monthly_kwh(25.0, hours=720.0, psu_efficiency=1.0)
        assert result == pytest.approx(18.0)

    def test_psu_efficiency_increases_draw(self):
        """Lower PSU efficiency should increase wall consumption."""
        perfect = estimate_monthly_kwh(25.0, psu_efficiency=1.0)
        lossy = estimate_monthly_kwh(25.0, psu_efficiency=0.9)
        assert lossy > perfect


class TestEstimateMonthlyCost:
    """Tests for estimate_monthly_cost."""

    def test_known_cost(self):
        """10 kWh at $0.10/kWh should cost $1.00."""
        assert estimate_monthly_cost(10.0, rate=0.10) == pytest.approx(1.0)

    def test_zero_consumption(self):
        """Zero consumption should cost nothing."""
        assert estimate_monthly_cost(0.0) == pytest.approx(0.0)


class TestForecastSummary:
    """Tests for forecast_summary."""

    def test_returns_expected_keys(self, sample_df_raw):
        """Verify all expected keys are present in the forecast."""
        result = forecast_summary(sample_df_raw)
        expected_keys = {
            "avg_total_watts",
            "avg_cpu_watts",
            "avg_gpu_watts",
            "wall_watts",
            "monthly_kwh",
            "monthly_cost_usd",
            "daily_kwh",
            "daily_cost_usd",
            "rate_per_kwh",
            "psu_efficiency",
        }
        assert set(result.keys()) == expected_keys

    def test_avg_total_watts(self, sample_df_raw):
        """Verify the average total watts is computed correctly."""
        result = forecast_summary(sample_df_raw)
        assert result["avg_total_watts"] == pytest.approx(23.2, abs=0.01)

    def test_cost_is_positive(self, sample_df_raw):
        """Monthly cost must be a positive number."""
        result = forecast_summary(sample_df_raw)
        assert result["monthly_cost_usd"] > 0

    def test_custom_rate(self, sample_df_raw):
        """Doubling the rate should double the cost."""
        base = forecast_summary(sample_df_raw, rate=0.10)
        double = forecast_summary(sample_df_raw, rate=0.20)
        assert double["monthly_cost_usd"] == pytest.approx(
            base["monthly_cost_usd"] * 2.0
        )


class TestComputeActualConsumption:
    """Tests for compute_actual_consumption."""

    def test_returns_expected_keys(self, sample_df_raw):
        """Verify all expected keys are present."""
        result = compute_actual_consumption(sample_df_raw)
        expected_keys = {
            "start",
            "end",
            "total_hours",
            "num_days",
            "actual_kwh",
            "actual_cost_usd",
            "rate_per_kwh",
            "daily_breakdown",
        }
        assert set(result.keys()) == expected_keys

    def test_actual_kwh_is_positive(self, sample_df_raw):
        """Actual kWh must be positive for non-zero data."""
        result = compute_actual_consumption(sample_df_raw)
        assert result["actual_kwh"] > 0

    def test_actual_cost_is_positive(self, sample_df_raw):
        """Actual cost must be positive for non-zero data."""
        result = compute_actual_consumption(sample_df_raw)
        assert result["actual_cost_usd"] > 0

    def test_daily_breakdown_has_columns(self, sample_df_raw):
        """Verify the daily breakdown DataFrame has expected columns."""
        import pandas as pd

        result = compute_actual_consumption(sample_df_raw)
        breakdown = result["daily_breakdown"]
        assert isinstance(breakdown, pd.DataFrame)
        expected_cols = {
            "daily_kwh",
            "daily_cost_usd",
            "cumulative_kwh",
            "cumulative_cost_usd",
        }
        assert set(breakdown.columns) == expected_cols

    def test_custom_rate_scales_cost(self, sample_df_raw):
        """Doubling the rate should double the actual cost."""
        base = compute_actual_consumption(sample_df_raw, rate=0.10)
        double = compute_actual_consumption(sample_df_raw, rate=0.20)
        assert double["actual_cost_usd"] == pytest.approx(
            base["actual_cost_usd"] * 2.0
        )

