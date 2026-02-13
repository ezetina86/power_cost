"""CLI entry point (placeholder for future use)."""

import logging

from power_cost.config import LOG_FORMAT, LOG_LEVEL

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the Power Cost application."""
    logger.info("Power Cost CLI -- not yet implemented, use Streamlit.")


if __name__ == "__main__":
    main()
