"""Tests for power_cost.app module."""

from unittest.mock import MagicMock, patch

import pandas as pd


class TestAppMain:
    """Tests for the app main function."""

    @patch("power_cost.app.render_dashboard")
    @patch("power_cost.app.get_data")
    @patch("power_cost.app.st")
    def test_main_success(self, mock_st, mock_get_data, mock_render):
        """Verify main loads data and calls render_dashboard."""
        from power_cost.app import main

        data = {
            "CPU_Watts": [4.0],
            "GPU_Watts": [19.0],
            "Total_Watts": [23.0],
        }
        index = pd.date_range("2026-02-13 10:00", periods=1, freq="1min")
        index.name = "Timestamp"
        mock_get_data.return_value = pd.DataFrame(data, index=index)

        main()

        mock_get_data.assert_called_once()
        mock_render.assert_called_once()

    @patch("power_cost.app.render_dashboard")
    @patch("power_cost.app.get_data")
    @patch("power_cost.app.st")
    def test_main_file_not_found(self, mock_st, mock_get_data, mock_render):
        """Verify main handles FileNotFoundError gracefully."""
        from power_cost.app import main

        mock_get_data.side_effect = FileNotFoundError("no file")

        main()

        mock_st.error.assert_called_once()
        mock_render.assert_not_called()

    @patch("power_cost.app.render_dashboard")
    @patch("power_cost.app.get_data")
    @patch("power_cost.app.st")
    def test_main_value_error(self, mock_st, mock_get_data, mock_render):
        """Verify main handles ValueError gracefully."""
        from power_cost.app import main

        mock_get_data.side_effect = ValueError("bad data")

        main()

        mock_st.error.assert_called_once()
        mock_render.assert_not_called()
