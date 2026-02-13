"""Tests for power_cost.data.models module."""

from datetime import datetime

from power_cost.data.models import PowerReading


class TestPowerReading:
    """Tests for the PowerReading dataclass."""

    def test_creation(self):
        """Verify a PowerReading can be created with valid values."""
        reading = PowerReading(
            timestamp=datetime(2026, 2, 13, 10, 0),
            cpu_watts=5.0,
            gpu_watts=20.0,
        )
        assert reading.cpu_watts == 5.0
        assert reading.gpu_watts == 20.0

    def test_total_watts(self):
        """Verify total_watts sums CPU and GPU."""
        reading = PowerReading(
            timestamp=datetime(2026, 2, 13, 10, 0),
            cpu_watts=4.0,
            gpu_watts=19.0,
        )
        assert reading.total_watts == 23.0

    def test_frozen(self):
        """Verify the reading is immutable."""
        import pytest

        reading = PowerReading(
            timestamp=datetime(2026, 2, 13, 10, 0),
            cpu_watts=4.0,
            gpu_watts=19.0,
        )
        with pytest.raises(AttributeError):
            reading.cpu_watts = 10.0  # type: ignore[misc]

    def test_zero_watts(self):
        """Verify zero power draw works correctly."""
        reading = PowerReading(
            timestamp=datetime(2026, 2, 13, 10, 0),
            cpu_watts=0.0,
            gpu_watts=0.0,
        )
        assert reading.total_watts == 0.0
