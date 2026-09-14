# FMS Similarity Island Workflow

This workflow evaluates DOCK6 Similarity Island clustering using the Footprint Matching Score (FMS) over a series of clustering cutoffs.

The purpose is to treat the cutoff scan as a reproducible computational experiment and measure how FMS cutoff affects cluster formation, cluster size, computational cost, runtime, throughput, and memory use.

The default FMS cutoffs are:

    0
    1
    3
    5
    7
    10
    15
    20

All calculations use the same molecular library and DOCK6 scoring configuration. Only `similarity_island_fms_cutoff` changes between calculations.

## Scripts

`000.config.sh`

Stores the FMS cutoffs, DOCK6 paths, molecular library, grid files, parameter files, and SLURM settings.

Run:

    ./000.config.sh

`001.setup_FMS_runs.sh`

Validates the required files and generates one FMS DOCK input for every cutoff.

Run:

    ./001.setup_FMS_runs.sh

`002.make_task_list.sh`

Creates `FMS_tasks.tsv`, which records every cutoff calculation.

Run:

    ./002.make_task_list.sh

`003.run_one_task.slurm`

Runs one FMS cutoff calculation. This script is normally called by the chunk runner.

Manual example:

    ./003.run_one_task.slurm 1

`004.run_FMS_chunks.slurm`

Runs multiple independent serial FMS calculations concurrently on one allocated node.

This script is normally submitted through `005.submit_FMS.sh`.

`005.submit_FMS.sh`

Submits the complete FMS cutoff experiment to SLURM.

Run:

    ./005.submit_FMS.sh

`006.collect_FMS_results.py`

Checks completion and extracts the experimental results from every successful FMS output.

Run:

    python3 006.collect_FMS_results.py

It creates:

    FMS_status.csv
    FMS_analysis_summary.csv
    FMS_island_statistics.csv
    FMS_member_statistics.csv
    FMS_island_calculations.csv

`FMS_analysis_summary.csv` contains one row per cutoff and includes the main quantities needed for comparing the experiments:

    cutoff
    molecules_to_cluster
    molecules_clustered
    total_islands
    largest_island
    smallest_island
    mean_island_size
    median_island_size
    std_island_size
    singleton_islands
    singleton_fraction
    largest_island_fraction
    total_fms_calculations
    average_fms_calculations_per_island
    mean_member_fms
    median_member_fms
    std_member_fms
    min_member_fms
    max_member_fms
    elapsed_seconds
    molecules_per_second
    virtual_memory_kb
    physical_memory_kb

FMS values from island heads are excluded from member statistics because the head value is the self-comparison value of 0.0000.

`007.analyze_FMS_results.py`

Reads `FMS_analysis_summary.csv` and displays the cutoff experiment in a compact comparative form.

Run:

    python3 007.analyze_FMS_results.py

The CSV data are structured so that cutoff can later be plotted against quantities such as number of islands, cluster size, singleton fraction, FMS score, total FMS calculations, runtime, throughput, and memory.

## Normal Workflow

Run the scripts in order:

    ./001.setup_FMS_runs.sh
    ./002.make_task_list.sh
    ./005.submit_FMS.sh

After the calculations finish:

    python3 006.collect_FMS_results.py
    python3 007.analyze_FMS_results.py

The main experimental dataset for cutoff-level comparison is:

    FMS_analysis_summary.csv
