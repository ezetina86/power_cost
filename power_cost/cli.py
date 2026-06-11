"""CLI entry point for Power Cost analysis."""

import argparse
import logging
import sys
from pathlib import Path

from power_cost.analysis.forecast import forecast_summary
from power_cost.analysis.stats import compute_summary_stats
from power_cost.config import (
    ELECTRICITY_RATE_PER_KWH,
    LOG_FORMAT,
    LOG_LEVEL,
    LOG_PATH,
    PSU_EFFICIENCY,
)
from power_cost.data.loader import load_power_log

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the Power Cost CLI."""
    parser = argparse.ArgumentParser(
        description="Analyse laptop power consumption logs and forecast monthly cost."
    )
    parser.add_argument(
        "--path", type=Path, default=LOG_PATH, help="Path to the power monitor CSV log."
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=ELECTRICITY_RATE_PER_KWH,
        help="Electricity rate in USD per kWh.",
    )
    parser.add_argument(
        "--efficiency",
        type=float,
        default=PSU_EFFICIENCY,
        help="PSU efficiency factor (0-1).",
    )

    args = parser.parse_args()

    try:
        df = load_power_log(args.path)
    except (FileNotFoundError, ValueError) as e:
        logger.error("Failed to load power log: %s", e)
        sys.exit(1)

    stats = compute_summary_stats(df)
    forecast = forecast_summary(df, rate=args.rate, psu_efficiency=args.efficiency)

    print("\n" + "=" * 40)
    print(" POWER COST ANALYSIS SUMMARY ")
    print("=" * 40)
    print(f"Data Points:    {len(df)}")
    print(f"Start:          {df.index.min()}")
    print(f"End:            {df.index.max()}")
    print("-" * 40)
    print("AVERAGE POWER DRAW (Watts):")
    print(f"  CPU:          {stats['cpu']['mean']:.2f} W")
    print(f"  GPU:          {stats['gpu']['mean']:.2f} W")
    print(f"  Total:        {stats['total']['mean']:.2f} W")
    print(
        f"  At Wall:      {forecast['wall_watts']:.2f} W "
        f"(eff: {args.efficiency:.0%})"
    )
    print("-" * 40)
    print("FORECAST (24/7 Running):")
    print(f"  Monthly kWh:  {forecast['monthly_kwh']:.2f} kWh")
    print(
        f"  Monthly Cost: ${forecast['monthly_cost_usd']:.2f} "
        f"(@ ${args.rate:.4f}/kWh)"
    )
    print("=" * 40 + "\n")


if __name__ == "__main__":
    main()
