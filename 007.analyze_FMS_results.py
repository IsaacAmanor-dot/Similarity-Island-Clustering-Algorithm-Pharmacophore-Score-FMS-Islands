#!/usr/bin/env python3

import csv
import math
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

SUMMARY_CSV = SCRIPT_DIR / "FMS_analysis_summary.csv"


def number(value):
    try:
        value = float(value)

        if math.isfinite(value):
            return value

    except (TypeError, ValueError):
        pass

    return math.nan


def main():
    if not SUMMARY_CSV.is_file():
        print(
            f"ERROR: Missing {SUMMARY_CSV.name}. "
            "Run 006.collect_FMS_results.py first."
        )
        sys.exit(1)

    with SUMMARY_CSV.open(
        newline="",
    ) as handle:

        rows = list(
            csv.DictReader(handle)
        )

    if not rows:
        print(
            f"ERROR: {SUMMARY_CSV.name} "
            "contains no experimental results."
        )
        sys.exit(1)

    rows.sort(
        key=lambda row: number(
            row["cutoff"]
        )
    )

    print()
    print(
        "FMS Similarity Island cutoff experiment"
    )
    print()

    print(
        "Cutoff  Islands  Largest  Mean size  "
        "Singletons  Mean FMS  Time (s)  "
        "FMS calculations"
    )

    for row in rows:
        print(
            f"{number(row['cutoff']):>6.2f} "
            f"{int(float(row['total_islands'])):>8d} "
            f"{int(float(row['largest_island'])):>8d} "
            f"{number(row['mean_island_size']):>10.2f} "
            f"{int(float(row['singleton_islands'])):>10d} "
            f"{number(row['mean_member_fms']):>9.3f} "
            f"{number(row['elapsed_seconds']):>9.3f} "
            f"{int(float(row['total_fms_calculations'])):>16d}"
        )

    print()
    print("Experimental variables available for plotting:")
    print()
    print("  cutoff vs total_islands")
    print("  cutoff vs largest_island")
    print("  cutoff vs mean_island_size")
    print("  cutoff vs median_island_size")
    print("  cutoff vs singleton_islands")
    print("  cutoff vs singleton_fraction")
    print("  cutoff vs mean_member_fms")
    print("  cutoff vs median_member_fms")
    print("  cutoff vs total_fms_calculations")
    print(
        "  cutoff vs "
        "average_fms_calculations_per_island"
    )
    print("  cutoff vs elapsed_seconds")
    print("  cutoff vs molecules_per_second")
    print("  cutoff vs virtual_memory_kb")
    print("  cutoff vs physical_memory_kb")
    print()
    print(
        "Plot generation is intentionally "
        "separate from raw DOCK parsing."
    )
    print()


if __name__ == "__main__":
    main()
