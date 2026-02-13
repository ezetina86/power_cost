"""CSV data loader and validation for power monitor logs."""

import logging
from pathlib import Path

import pandas as pd

from power_cost.config import LOG_PATH

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS: list[str] = ["Timestamp", "CPU_Watts", "GPU_Watts"]


def load_power_log(path: Path | None = None) -> pd.DataFrame:
    """Load and validate the power monitor CSV log.

    Args:
        path: Path to the CSV file. Defaults to ``config.LOG_PATH``.

    Returns:
        A validated DataFrame with a ``Total_Watts`` column appended.

    Raises:
        FileNotFoundError: If the log file does not exist.
        ValueError: If required columns are missing or data is invalid.
    """
    if path is None:
        path = LOG_PATH

    if not path.exists():
        msg = f"Power log not found: {path}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    logger.info("Loading power log from %s", path)
    df = pd.read_csv(path)

    _validate_columns(df)
    df = _parse_timestamps(df)
    df = _validate_values(df)
    df["Total_Watts"] = df["CPU_Watts"] + df["GPU_Watts"]

    logger.info("Loaded %d readings", len(df))
    return df


def _validate_columns(df: pd.DataFrame) -> None:
    """Ensure the DataFrame contains the expected columns.

    Args:
        df: Raw DataFrame to check.

    Raises:
        ValueError: If any required column is missing.
    """
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        msg = f"Missing required columns: {missing}"
        logger.error(msg)
        raise ValueError(msg)


def _parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the Timestamp column to datetime and set as index.

    Args:
        df: DataFrame with a string Timestamp column.

    Returns:
        DataFrame with a DatetimeIndex.
    """
    df = df.copy()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.set_index("Timestamp")
    return df


def _validate_values(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with null or negative power values.

    Args:
        df: DataFrame to validate.

    Returns:
        Cleaned DataFrame.
    """
    initial_len = len(df)
    df = df.dropna(subset=["CPU_Watts", "GPU_Watts"])

    # Drop rows with negative watt values.
    mask = (df["CPU_Watts"] >= 0) & (df["GPU_Watts"] >= 0)
    df = df[mask]

    dropped = initial_len - len(df)
    if dropped > 0:
        logger.warning("Dropped %d invalid rows", dropped)

    return df
