"""Tests for the power_cost.data.loader module."""

import pandas as pd
import pytest

from power_cost.data.loader import load_power_log


class TestLoadPowerLog:
    """Tests for load_power_log."""

    def test_loads_valid_csv(self, sample_csv):
        """Verify a valid CSV produces a DataFrame with expected columns."""
        df = load_power_log(sample_csv)
        assert isinstance(df, pd.DataFrame)
        assert "CPU_Watts" in df.columns
        assert "GPU_Watts" in df.columns
        assert "Total_Watts" in df.columns

    def test_total_watts_computed(self, sample_csv):
        """Verify Total_Watts equals CPU_Watts + GPU_Watts."""
        df = load_power_log(sample_csv)
        expected = df["CPU_Watts"] + df["GPU_Watts"]
        pd.testing.assert_series_equal(
            df["Total_Watts"], expected, check_names=False
        )

    def test_datetime_index(self, sample_csv):
        """Verify the index is a DatetimeIndex."""
        df = load_power_log(sample_csv)
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_row_count(self, sample_csv):
        """Verify the correct number of rows are loaded."""
        df = load_power_log(sample_csv)
        assert len(df) == 10

    def test_file_not_found(self, tmp_path):
        """Verify FileNotFoundError on missing file."""
        with pytest.raises(FileNotFoundError):
            load_power_log(tmp_path / "nonexistent.csv")

    def test_missing_columns(self, tmp_path):
        """Verify ValueError when required columns are missing."""
        csv_path = tmp_path / "bad.csv"
        csv_path.write_text("Time,Watts\n10:00,5\n")
        with pytest.raises(ValueError, match="Usecols do not match columns"):
            load_power_log(csv_path)

    def test_drops_negative_values(self, tmp_path):
        """Verify rows with negative wattage are dropped."""
        csv_path = tmp_path / "neg.csv"
        csv_path.write_text(
            "Timestamp,CPU_Watts,GPU_Watts\n"
            "2026-02-13 10:00:00,4.0,19.0\n"
            "2026-02-13 10:01:00,-1.0,18.0\n"
            "2026-02-13 10:02:00,3.0,-5.0\n"
        )
        df = load_power_log(csv_path)
        assert len(df) == 1

    def test_drops_null_values(self, tmp_path):
        """Verify rows with null wattage are dropped."""
        csv_path = tmp_path / "null.csv"
        csv_path.write_text(
            "Timestamp,CPU_Watts,GPU_Watts\n"
            "2026-02-13 10:00:00,4.0,19.0\n"
            "2026-02-13 10:01:00,,18.0\n"
            "2026-02-13 10:02:00,3.0,\n"
        )
        df = load_power_log(csv_path)
        assert len(df) == 1
