"""Data models and schemas for power consumption readings."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PowerReading:
    """A single power consumption measurement.

    Attributes:
        timestamp: When the measurement was taken.
        cpu_watts: CPU power draw in watts.
        gpu_watts: GPU power draw in watts.
    """

    timestamp: datetime
    cpu_watts: float
    gpu_watts: float

    @property
    def total_watts(self) -> float:
        """Return the combined CPU + GPU power draw."""
        return self.cpu_watts + self.gpu_watts
