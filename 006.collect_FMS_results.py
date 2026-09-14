#!/usr/bin/env python3

import csv
import math
import re
import statistics
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

TASK_LIST = SCRIPT_DIR / "FMS_tasks.tsv"

STATUS_CSV = SCRIPT_DIR / "FMS_status.csv"
SUMMARY_CSV = SCRIPT_DIR / "FMS_analysis_summary.csv"
ISLAND_CSV = SCRIPT_DIR / "FMS_island_statistics.csv"
MEMBER_CSV = SCRIPT_DIR / "FMS_member_statistics.csv"
CALCULATIONS_CSV = SCRIPT_DIR / "FMS_island_calculations.csv"


def mean(values):
    return statistics.mean(values) if values else math.nan


def median(values):
    return statistics.median(values) if values else math.nan


def pstdev(values):
    if len(values) > 1:
        return statistics.pstdev(values)

    if len(values) == 1:
        return 0.0

    return math.nan


def minimum(values):
    return min(values) if values else math.nan


def maximum(values):
    return max(values) if values else math.nan


def read_tasks():
    if not TASK_LIST.is_file():
        raise SystemExit(
            "ERROR: FMS_tasks.tsv not found. "
            "Run 002.make_task_list.sh first."
        )

    with TASK_LIST.open(newline="") as handle:
        reader = csv.DictReader(
            handle,
            delimiter="\t",
        )

        return list(reader)


def parse_output(output_file):
    run = {
        "source_file": str(output_file),
        "completed": False,
        "cutoff": math.nan,
        "molecules_to_cluster": 0,
        "molecules_clustered": 0,
        "total_islands": 0,
        "total_fms_calculations": 0,
        "average_fms_calculations_per_island": math.nan,
        "elapsed_seconds": math.nan,
        "molecules_per_second": math.nan,
        "virtual_memory_kb": 0,
        "physical_memory_kb": 0,
        "islands": [],
        "calculation_table": {},
    }

    current = None
    in_calculation_table = False

    cutoff_re = re.compile(
        r"^Similarity Cutoff:\s*"
        r"([-+]?\d+(?:\.\d+)?)"
    )

    molecules_to_cluster_re = re.compile(
        r"^Molecules to Cluster:\s*(\d+)"
    )

    island_re = re.compile(
        r"^FMS ISLAND\s+(\d+)"
    )

    head_re = re.compile(
        r"^Island Head:\s+(\S+)"
    )

    size_re = re.compile(
        r"^Island Size:\s+(\d+)"
    )

    member_re = re.compile(
        r"^\s*(\d+)\s+"
        r"(\S+)\s+"
        r"([-+]?\d+(?:\.\d+)?)\s+"
        r"(HEAD|MEMBER)\s*$"
    )

    molecules_clustered_re = re.compile(
        r"^Molecules Clustered:\s*(\d+)"
    )

    total_islands_re = re.compile(
        r"^Total Islands:\s*(\d+)"
    )

    total_calculations_re = re.compile(
        r"^Total FMS Calculations:\s*(\d+)"
    )

    average_calculations_re = re.compile(
        r"^Average FMS Calculations per Island:\s*"
        r"([-+]?\d+(?:\.\d+)?)"
    )

    calculation_row_re = re.compile(
        r"^\s*(\d+)\s+(\d+)\s+(\d+)\s*$"
    )

    elapsed_re = re.compile(
        r"^Total elapsed time:\s*"
        r"([-+]?\d+(?:\.\d+)?)\s+seconds"
    )

    rate_re = re.compile(
        r"^Number of molecules per second:\s*"
        r"([-+]?\d+(?:\.\d+)?)"
    )

    virtual_re = re.compile(
        r"^Virtual memory used for this process:\s*"
        r"(\d+)\s+kilobytes"
    )

    physical_re = re.compile(
        r"^Physical memory used for this process:\s*"
        r"(\d+)\s+kilobytes"
    )

    with output_file.open(
        "r",
        errors="replace",
    ) as handle:

        for raw_line in handle:
            line = raw_line.strip()

            match = cutoff_re.match(line)

            if match:
                run["cutoff"] = float(
                    match.group(1)
                )
                continue

            match = molecules_to_cluster_re.match(line)

            if match:
                run["molecules_to_cluster"] = int(
                    match.group(1)
                )
                continue

            match = island_re.match(line)

            if match:
                in_calculation_table = False

                current = {
                    "island_id": int(
                        match.group(1)
                    ),
                    "head": "",
                    "size": 0,
                    "members": [],
                }

                run["islands"].append(current)
                continue

            if current is not None:
                match = head_re.match(line)

                if match:
                    current["head"] = match.group(1)
                    continue

                match = size_re.match(line)

                if match:
                    current["size"] = int(
                        match.group(1)
                    )
                    continue

                match = member_re.match(line)

                if match:
                    rank = int(match.group(1))
                    molecule = match.group(2)
                    score = float(match.group(3))
                    role = match.group(4)

                    if role == "MEMBER":
                        current["members"].append(
                            {
                                "rank": rank,
                                "molecule": molecule,
                                "fms": score,
                            }
                        )

                    continue

            if line.startswith(
                "Similarity Island clustering complete"
            ):
                run["completed"] = True
                current = None
                continue

            match = molecules_clustered_re.match(line)

            if match:
                run["molecules_clustered"] = int(
                    match.group(1)
                )
                continue

            match = total_islands_re.match(line)

            if match:
                run["total_islands"] = int(
                    match.group(1)
                )
                continue

            match = total_calculations_re.match(line)

            if match:
                run["total_fms_calculations"] = int(
                    match.group(1)
                )
                continue

            match = average_calculations_re.match(line)

            if match:
                run[
                    "average_fms_calculations_per_island"
                ] = float(match.group(1))
                continue

            if line.startswith(
                "Similarity Island Calculations by FMS:"
            ):
                in_calculation_table = True
                continue

            if in_calculation_table:
                if line.startswith(
                    "Rescoring Analysis molecules"
                ):
                    in_calculation_table = False
                    continue

                match = calculation_row_re.match(line)

                if match:
                    island_id = int(match.group(1))

                    run["calculation_table"][
                        island_id
                    ] = {
                        "calculations": int(
                            match.group(2)
                        ),
                        "molecules": int(
                            match.group(3)
                        ),
                    }

                    continue

            match = elapsed_re.match(line)

            if match:
                run["elapsed_seconds"] = float(
                    match.group(1)
                )
                continue

            match = rate_re.match(line)

            if match:
                run["molecules_per_second"] = float(
                    match.group(1)
                )
                continue

            match = virtual_re.match(line)

            if match:
                run["virtual_memory_kb"] = int(
                    match.group(1)
                )
                continue

            match = physical_re.match(line)

            if match:
                run["physical_memory_kb"] = int(
                    match.group(1)
                )
                continue

    return run


def calculate_statistics(run):
    island_sizes = [
        island["size"]
        for island in run["islands"]
        if island["size"] > 0
    ]

    all_fms = []

    for island in run["islands"]:
        scores = [
            member["fms"]
            for member in island["members"]
        ]

        all_fms.extend(scores)

        island["member_count"] = len(scores)

        island["mean_member_fms"] = mean(scores)
        island["median_member_fms"] = median(scores)
        island["std_member_fms"] = pstdev(scores)
        island["min_member_fms"] = minimum(scores)
        island["max_member_fms"] = maximum(scores)

    run["largest_island"] = (
        maximum(island_sizes)
        if island_sizes
        else 0
    )

    run["smallest_island"] = (
        minimum(island_sizes)
        if island_sizes
        else 0
    )

    run["mean_island_size"] = mean(island_sizes)
    run["median_island_size"] = median(island_sizes)
    run["std_island_size"] = pstdev(island_sizes)

    run["singleton_islands"] = sum(
        size == 1
        for size in island_sizes
    )

    if run["total_islands"] > 0:
        run["singleton_fraction"] = (
            run["singleton_islands"]
            / run["total_islands"]
        )
    else:
        run["singleton_fraction"] = math.nan

    if run["molecules_clustered"] > 0:
        run["largest_island_fraction"] = (
            run["largest_island"]
            / run["molecules_clustered"]
        )
    else:
        run["largest_island_fraction"] = math.nan

    run["member_fms_count"] = len(all_fms)
    run["mean_member_fms"] = mean(all_fms)
    run["median_member_fms"] = median(all_fms)
    run["std_member_fms"] = pstdev(all_fms)
    run["min_member_fms"] = minimum(all_fms)
    run["max_member_fms"] = maximum(all_fms)


def validate_run(run):
    problems = []

    if not run["completed"]:
        problems.append(
            "completion marker missing"
        )

    parsed_islands = len(run["islands"])

    if (
        run["total_islands"] > 0
        and parsed_islands
        != run["total_islands"]
    ):
        problems.append(
            f"islands parsed={parsed_islands} "
            f"reported={run['total_islands']}"
        )

    parsed_molecules = sum(
        island["size"]
        for island in run["islands"]
    )

    if (
        run["molecules_clustered"] > 0
        and parsed_molecules
        != run["molecules_clustered"]
    ):
        problems.append(
            f"molecules parsed={parsed_molecules} "
            f"reported={run['molecules_clustered']}"
        )

    return problems


def write_csv(path, fields, rows):
    with path.open(
        "w",
        newline="",
    ) as handle:

        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(row)


def main():
    tasks = read_tasks()

    status_rows = []
    runs = []

    for task in tasks:
        case_name = task["case_name"]

        output_file = (
            SCRIPT_DIR
            / f"{case_name}.out"
        )

        summary_file = (
            SCRIPT_DIR
            / f"{case_name}_summary.out"
        )

        success_file = (
            SCRIPT_DIR
            / f".{case_name}.success"
        )

        failed_file = (
            SCRIPT_DIR
            / f".{case_name}.failed"
        )

        if output_file.is_file():
            run = parse_output(output_file)
        else:
            run = None

        if (
            success_file.is_file()
            and run is not None
            and run["completed"]
            and summary_file.is_file()
            and summary_file.stat().st_size > 0
        ):
            status = "SUCCESS"

        elif failed_file.is_file():
            status = "FAILED"

        elif output_file.is_file():
            status = "INCOMPLETE"

        else:
            status = "MISSING"

        status_rows.append(
            {
                "task_id": task["task_id"],
                "cutoff": task["cutoff"],
                "case_name": case_name,
                "status": status,
                "total_islands": (
                    run["total_islands"]
                    if run
                    else ""
                ),
                "elapsed_seconds": (
                    run["elapsed_seconds"]
                    if run
                    else ""
                ),
                "output_file": str(output_file),
            }
        )

        if status != "SUCCESS":
            continue

        calculate_statistics(run)

        problems = validate_run(run)

        if problems:
            print(
                f"WARNING: {case_name}: "
                + "; ".join(problems)
            )

        run["case_name"] = case_name
        runs.append(run)

    status_fields = [
        "task_id",
        "cutoff",
        "case_name",
        "status",
        "total_islands",
        "elapsed_seconds",
        "output_file",
    ]

    write_csv(
        STATUS_CSV,
        status_fields,
        status_rows,
    )

    runs.sort(
        key=lambda run: run["cutoff"]
    )

    summary_fields = [
        "cutoff",
        "molecules_to_cluster",
        "molecules_clustered",
        "total_islands",
        "largest_island",
        "smallest_island",
        "mean_island_size",
        "median_island_size",
        "std_island_size",
        "singleton_islands",
        "singleton_fraction",
        "largest_island_fraction",
        "total_fms_calculations",
        "average_fms_calculations_per_island",
        "member_fms_count",
        "mean_member_fms",
        "median_member_fms",
        "std_member_fms",
        "min_member_fms",
        "max_member_fms",
        "elapsed_seconds",
        "molecules_per_second",
        "virtual_memory_kb",
        "physical_memory_kb",
        "case_name",
        "source_file",
    ]

    summary_rows = []

    for run in runs:
        summary_rows.append(
            {
                field: run.get(field, "")
                for field in summary_fields
            }
        )

    write_csv(
        SUMMARY_CSV,
        summary_fields,
        summary_rows,
    )

    island_fields = [
        "cutoff",
        "island_id",
        "island_head",
        "island_size",
        "member_count",
        "mean_member_fms",
        "median_member_fms",
        "std_member_fms",
        "min_member_fms",
        "max_member_fms",
        "fms_calculations",
    ]

    island_rows = []

    member_fields = [
        "cutoff",
        "island_id",
        "island_head",
        "island_size",
        "rank",
        "molecule",
        "fms",
    ]

    member_rows = []

    calculation_fields = [
        "cutoff",
        "island_id",
        "island_size",
        "fms_calculations",
        "molecules",
    ]

    calculation_rows = []

    for run in runs:
        for island in run["islands"]:
            island_id = island["island_id"]

            calculation = (
                run["calculation_table"]
                .get(
                    island_id,
                    {},
                )
            )

            island_rows.append(
                {
                    "cutoff": run["cutoff"],
                    "island_id": island_id,
                    "island_head": island["head"],
                    "island_size": island["size"],
                    "member_count": (
                        island["member_count"]
                    ),
                    "mean_member_fms": (
                        island["mean_member_fms"]
                    ),
                    "median_member_fms": (
                        island["median_member_fms"]
                    ),
                    "std_member_fms": (
                        island["std_member_fms"]
                    ),
                    "min_member_fms": (
                        island["min_member_fms"]
                    ),
                    "max_member_fms": (
                        island["max_member_fms"]
                    ),
                    "fms_calculations": (
                        calculation.get(
                            "calculations",
                            "",
                        )
                    ),
                }
            )

            if calculation:
                calculation_rows.append(
                    {
                        "cutoff": run["cutoff"],
                        "island_id": island_id,
                        "island_size": (
                            island["size"]
                        ),
                        "fms_calculations": (
                            calculation[
                                "calculations"
                            ]
                        ),
                        "molecules": (
                            calculation[
                                "molecules"
                            ]
                        ),
                    }
                )

            for member in island["members"]:
                member_rows.append(
                    {
                        "cutoff": run["cutoff"],
                        "island_id": island_id,
                        "island_head": (
                            island["head"]
                        ),
                        "island_size": (
                            island["size"]
                        ),
                        "rank": member["rank"],
                        "molecule": (
                            member["molecule"]
                        ),
                        "fms": member["fms"],
                    }
                )

    write_csv(
        ISLAND_CSV,
        island_fields,
        island_rows,
    )

    write_csv(
        MEMBER_CSV,
        member_fields,
        member_rows,
    )

    write_csv(
        CALCULATIONS_CSV,
        calculation_fields,
        calculation_rows,
    )

    success = sum(
        row["status"] == "SUCCESS"
        for row in status_rows
    )

    failed = sum(
        row["status"] == "FAILED"
        for row in status_rows
    )

    incomplete = sum(
        row["status"] == "INCOMPLETE"
        for row in status_rows
    )

    missing = sum(
        row["status"] == "MISSING"
        for row in status_rows
    )

    print()
    print("FMS Similarity Island experiment")
    print()
    print(f"Total tasks:  {len(status_rows)}")
    print(f"Successful:   {success}")
    print(f"Failed:       {failed}")
    print(f"Incomplete:   {incomplete}")
    print(f"Missing:      {missing}")
    print()

    if runs:
        print(
            "Cutoff  Islands  Largest  Mean size  "
            "Mean FMS  Time (s)  Calculations"
        )

        for run in runs:
            print(
                f"{run['cutoff']:>6.2f} "
                f"{run['total_islands']:>8d} "
                f"{run['largest_island']:>8d} "
                f"{run['mean_island_size']:>10.2f} "
                f"{run['mean_member_fms']:>9.3f} "
                f"{run['elapsed_seconds']:>9.3f} "
                f"{run['total_fms_calculations']:>13d}"
            )

    print()
    print("CSV files:")
    print(f"  {STATUS_CSV.name}")
    print(f"  {SUMMARY_CSV.name}")
    print(f"  {ISLAND_CSV.name}")
    print(f"  {MEMBER_CSV.name}")
    print(f"  {CALCULATIONS_CSV.name}")
    print()


if __name__ == "__main__":
    main()
