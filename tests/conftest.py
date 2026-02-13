"""Shared test fixtures for the power_cost test suite."""

import pandas as pd
import pytest


@pytest.fixture()
def sample_csv(tmp_path):
    """Create a temporary CSV file with realistic power data."""
    csv_path = tmp_path / "power_monitor.log"
    csv_path.write_text(
        "Timestamp,CPU_Watts,GPU_Watts\n"
        "2026-02-13 10:00:00,4.00,19.00\n"
        "2026-02-13 10:01:00,3.50,18.50\n"
        "2026-02-13 10:02:00,5.00,20.00\n"
        "2026-02-13 10:03:00,3.80,19.20\n"
        "2026-02-13 10:04:00,4.20,18.80\n"
        "2026-02-13 11:00:00,6.00,21.00\n"
        "2026-02-13 11:01:00,5.50,20.50\n"
        "2026-02-13 11:02:00,7.00,22.00\n"
        "2026-02-13 12:00:00,3.00,17.00\n"
        "2026-02-13 12:01:00,3.20,17.50\n"
    )
    return csv_path


@pytest.fixture()
def sample_df(sample_csv):
    """Return a validated DataFrame built from sample CSV data."""
    from power_cost.data.loader import load_power_log

    return load_power_log(sample_csv)


@pytest.fixture()
def sample_df_raw():
    """Return a small in-memory DataFrame for unit tests."""
    data = {
        "CPU_Watts": [4.0, 3.5, 5.0, 3.8, 4.2],
        "GPU_Watts": [19.0, 18.5, 20.0, 19.2, 18.8],
        "Total_Watts": [23.0, 22.0, 25.0, 23.0, 23.0],
    }
    index = pd.date_range("2026-02-13 10:00", periods=5, freq="1min")
    index.name = "Timestamp"
    return pd.DataFrame(data, index=index)
