"""Tests for power_cost.cli module."""

from typing import Any
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from power_cost.cli import main


class TestCLIMain:
    """Tests for the CLI main function."""

    @pytest.fixture  # type: ignore
    def mock_df(self) -> pd.DataFrame:
        """Create a mock DataFrame for testing."""
        df = pd.DataFrame(
            {
                "CPU_Watts": [10.0, 20.0],
                "GPU_Watts": [5.0, 15.0],
                "Total_Watts": [15.0, 35.0],
            },
            index=pd.to_datetime(["2024-01-01 00:00:00", "2024-01-01 00:01:00"]),
        )
        df.index.name = "Timestamp"
        return df

    @patch("power_cost.cli.load_power_log")
    @patch("power_cost.cli.compute_summary_stats")
    @patch("power_cost.cli.forecast_summary")
    @patch("argparse.ArgumentParser.parse_args")
    def test_main_success(
        self,
        mock_parse_args: MagicMock,
        mock_forecast: MagicMock,
        mock_stats: MagicMock,
        mock_load: MagicMock,
        mock_df: pd.DataFrame,
        capsys: Any,
    ) -> None:
        """Verify main() runs successfully and prints summary."""
        # Setup mocks
        mock_parse_args.return_value = MagicMock(
            path="dummy.csv", rate=0.15, efficiency=0.9
        )
        mock_load.return_value = mock_df
        mock_stats.return_value = {
            "cpu": {"mean": 15.0},
            "gpu": {"mean": 10.0},
            "total": {"mean": 25.0},
        }
        mock_forecast.return_value = {
            "wall_watts": 27.78,
            "monthly_kwh": 20.0,
            "monthly_cost_usd": 3.0,
        }

        # Run main
        main()

        # Check output
        captured = capsys.readouterr()
        assert "POWER COST ANALYSIS SUMMARY" in captured.out
        assert "Data Points:    2" in captured.out
        assert "CPU:          15.00 W" in captured.out
        assert "Monthly Cost: $3.00" in captured.out

        # Verify calls
        mock_load.assert_called_once()
        mock_stats.assert_called_once_with(mock_df)
        mock_forecast.assert_called_once_with(mock_df, rate=0.15, psu_efficiency=0.9)

    @patch("power_cost.cli.load_power_log")
    @patch("argparse.ArgumentParser.parse_args")
    def test_main_file_not_found(
        self, mock_parse_args: MagicMock, mock_load: MagicMock
    ) -> None:
        """Verify main() exits with 1 if file is not found."""
        mock_parse_args.return_value = MagicMock(
            path="missing.csv", rate=0.15, efficiency=0.9
        )
        mock_load.side_effect = FileNotFoundError("File not found")

        with patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)

    @patch("power_cost.cli.load_power_log")
    @patch("argparse.ArgumentParser.parse_args")
    def test_main_invalid_value(
        self, mock_parse_args: MagicMock, mock_load: MagicMock
    ) -> None:
        """Verify main() exits with 1 if log data is invalid."""
        mock_parse_args.return_value = MagicMock(
            path="invalid.csv", rate=0.15, efficiency=0.9
        )
        mock_load.side_effect = ValueError("Invalid data")

        with patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)
