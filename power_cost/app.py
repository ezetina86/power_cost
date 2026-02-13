"""Streamlit application entry point.

Run with:
    uv run streamlit run power_cost/app.py
"""

import logging
from pathlib import Path

import pandas as pd
import streamlit as st

from power_cost.config import LOG_FORMAT, LOG_LEVEL, LOG_PATH
from power_cost.data.loader import load_power_log
from power_cost.ui.dashboard import render_dashboard

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Power Cost",
    page_icon="",
    layout="wide",
)


@st.cache_data
def get_data(path: Path) -> pd.DataFrame:
    """Load data with caching to avoid expensive I/O on every rerun.

    Args:
        path: Path to the CSV file.

    Returns:
        The loaded DataFrame.
    """
    return load_power_log(path)


def main() -> None:
    """Load data and render the dashboard."""
    try:
        # Use cached loader to improve performance
        df = get_data(LOG_PATH)
    except (FileNotFoundError, ValueError):
        logger.exception("Failed to load power log")
        st.error(
            "Could not load the power monitor log. "
            "Please check that the file exists and is valid."
        )
        return

    render_dashboard(df)


if __name__ == "__main__":
    main()
