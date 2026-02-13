"""Configuration constants and project-wide settings."""

from pathlib import Path

# ---------------------------------------------------------------------------
# Data source
# ---------------------------------------------------------------------------
LOG_PATH: Path = Path(
    "/mnt/Data/scripts/power_monitor/logs/power_monitor.log"
)

# ---------------------------------------------------------------------------
# Electricity pricing (February 2026 bill)
# ---------------------------------------------------------------------------
ELECTRICITY_RATE_PER_KWH: float = 0.1587  # USD per kWh (incl. TVA adj.)

# ---------------------------------------------------------------------------
# Forecasting assumptions
# ---------------------------------------------------------------------------
HOURS_PER_DAY: int = 24
DAYS_PER_MONTH: int = 30
HOURS_PER_MONTH: float = HOURS_PER_DAY * DAYS_PER_MONTH  # 720.0

# PSU efficiency: wall watts vs. what components actually draw.
# Typical laptop PSU efficiency is around 85-90 %.
PSU_EFFICIENCY: float = 0.90

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FORMAT: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
LOG_LEVEL: str = "INFO"
