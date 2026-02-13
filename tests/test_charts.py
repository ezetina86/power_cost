"""Tests for power_cost.ui.charts module."""

import plotly.graph_objects as go

from power_cost.ui.charts import (
    plot_cost_breakdown,
    plot_cpu_vs_gpu,
    plot_hourly_distribution,
    plot_power_over_time,
)


class TestPlotPowerOverTime:
    """Tests for plot_power_over_time."""

    def test_returns_figure(self, sample_df_raw):
        """Verify the function returns a Plotly Figure."""
        fig = plot_power_over_time(sample_df_raw)
        assert isinstance(fig, go.Figure)

    def test_has_three_traces(self, sample_df_raw):
        """Verify the chart has CPU, GPU, and Total traces."""
        fig = plot_power_over_time(sample_df_raw)
        assert len(fig.data) == 3

    def test_trace_names(self, sample_df_raw):
        """Verify trace names are CPU, GPU, and Total."""
        fig = plot_power_over_time(sample_df_raw)
        names = {trace.name for trace in fig.data}
        assert names == {"CPU", "GPU", "Total"}


class TestPlotCpuVsGpu:
    """Tests for plot_cpu_vs_gpu."""

    def test_returns_figure(self, sample_df_raw):
        """Verify the function returns a Plotly Figure."""
        fig = plot_cpu_vs_gpu(sample_df_raw)
        assert isinstance(fig, go.Figure)

    def test_has_one_trace(self, sample_df_raw):
        """Verify the scatter chart has one trace."""
        fig = plot_cpu_vs_gpu(sample_df_raw)
        assert len(fig.data) == 1


class TestPlotHourlyDistribution:
    """Tests for plot_hourly_distribution."""

    def test_returns_figure(self, sample_df_raw):
        """Verify the function returns a Plotly Figure."""
        fig = plot_hourly_distribution(sample_df_raw)
        assert isinstance(fig, go.Figure)

    def test_has_bar_trace(self, sample_df_raw):
        """Verify the chart uses a bar trace."""
        fig = plot_hourly_distribution(sample_df_raw)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Bar)


class TestPlotCostBreakdown:
    """Tests for plot_cost_breakdown."""

    def test_returns_figure(self):
        """Verify the function returns a Plotly Figure."""
        forecast = {
            "avg_total_watts": 24.0,
            "avg_cpu_watts": 4.0,
            "avg_gpu_watts": 20.0,
            "wall_watts": 26.7,
            "monthly_kwh": 19.2,
            "monthly_cost_usd": 3.05,
            "daily_kwh": 0.64,
            "daily_cost_usd": 0.10,
            "rate_per_kwh": 0.1587,
            "psu_efficiency": 0.90,
        }
        fig = plot_cost_breakdown(forecast)
        assert isinstance(fig, go.Figure)

    def test_has_two_indicators(self):
        """Verify the chart has two indicator traces."""
        forecast = {
            "avg_total_watts": 24.0,
            "avg_cpu_watts": 4.0,
            "avg_gpu_watts": 20.0,
            "wall_watts": 26.7,
            "monthly_kwh": 19.2,
            "monthly_cost_usd": 3.05,
            "daily_kwh": 0.64,
            "daily_cost_usd": 0.10,
            "rate_per_kwh": 0.1587,
            "psu_efficiency": 0.90,
        }
        fig = plot_cost_breakdown(forecast)
        assert len(fig.data) == 2
