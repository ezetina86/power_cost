"""Tests for power_cost.ui.dashboard module."""

from unittest.mock import MagicMock, patch

import pandas as pd

from power_cost.ui.dashboard import render_metrics, render_sidebar


class TestRenderSidebar:
    """Tests for render_sidebar."""

    @patch("power_cost.ui.dashboard.st")
    def test_returns_tuple(self, mock_st):
        """Verify render_sidebar returns a (rate, efficiency) tuple."""
        mock_st.sidebar = MagicMock()
        mock_st.sidebar.number_input.return_value = 0.15
        mock_st.sidebar.slider.return_value = 90
        rate, eff = render_sidebar(0.1587, 0.90)
        assert isinstance(rate, float)
        assert isinstance(eff, float)

    @patch("power_cost.ui.dashboard.st")
    def test_efficiency_converted(self, mock_st):
        """Verify slider percentage is converted to a 0-1 float."""
        mock_st.sidebar = MagicMock()
        mock_st.sidebar.number_input.return_value = 0.15
        mock_st.sidebar.slider.return_value = 85
        _, eff = render_sidebar(0.1587, 0.90)
        assert eff == 0.85

    @patch("power_cost.ui.dashboard.st")
    def test_rate_passed_through(self, mock_st):
        """Verify the rate from number_input is returned as-is."""
        mock_st.sidebar = MagicMock()
        mock_st.sidebar.number_input.return_value = 0.25
        mock_st.sidebar.slider.return_value = 90
        rate, _ = render_sidebar(0.1587, 0.90)
        assert rate == 0.25


class TestRenderMetrics:
    """Tests for render_metrics."""

    @patch("power_cost.ui.dashboard.st")
    def test_calls_metric_four_times(self, mock_st):
        """Verify four metric cards are rendered."""
        cols = [MagicMock() for _ in range(4)]
        mock_st.columns.return_value = cols
        forecast = {
            "avg_total_watts": 24.0,
            "wall_watts": 26.7,
            "monthly_kwh": 19.2,
            "monthly_cost_usd": 3.05,
        }
        render_metrics(forecast)
        for col in cols:
            col.metric.assert_called_once()


class TestRenderDashboard:
    """Tests for render_dashboard."""

    @patch("power_cost.ui.dashboard.st")
    def test_render_dashboard_runs(self, mock_st):
        """Verify render_dashboard executes without error."""
        from power_cost.ui.dashboard import render_dashboard

        mock_st.sidebar = MagicMock()
        mock_st.sidebar.number_input.return_value = 0.15
        mock_st.sidebar.slider.return_value = 90

        # st.columns is called with varying counts; return enough mocks.
        mock_st.columns.side_effect = lambda n: [MagicMock() for _ in range(n)]

        # Expander must work as a context manager.
        expander_ctx = MagicMock()
        expander_ctx.__enter__ = MagicMock(return_value=MagicMock())
        expander_ctx.__exit__ = MagicMock(return_value=False)
        mock_st.expander.return_value = expander_ctx

        data = {
            "CPU_Watts": [4.0, 3.5, 5.0, 3.8, 4.2],
            "GPU_Watts": [19.0, 18.5, 20.0, 19.2, 18.8],
            "Total_Watts": [23.0, 22.0, 25.0, 23.0, 23.0],
        }
        index = pd.date_range("2026-02-13 10:00", periods=5, freq="1min")
        index.name = "Timestamp"
        df = pd.DataFrame(data, index=index)

        render_dashboard(df)

        mock_st.title.assert_called_once()
