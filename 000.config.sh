#!/bin/bash

CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

WORK_ROOT="${CONFIG_DIR}"

FMS_CUTOFFS=(
    0
    1
    3
    5
    7
    10
    15
    20
)

DOCK_ROOT="/gpfs/projects/rizzo/iamanor/DOCK6_Development/Similarity_Island/dock6_dev"
DOCK_BIN="${DOCK_ROOT}/bin/dock6"
DOCK_PARAMS="${DOCK_ROOT}/parameters"

VDW_DEFN_FILE="${DOCK_PARAMS}/vdw_AMBER_parm99.defn"
FLEX_DEFN_FILE="${DOCK_PARAMS}/flex.defn"
PH4_DEFN_FILE="${DOCK_PARAMS}/ph4.defn"

LIGAND_ATOM_FILE="/gpfs/projects/rizzo/iamanor/DOCK6_Development/Similarity_Island/TesTING_SMI_2/000_VS_For_DOCKING_SCORE/Dock_Scored_Molecules_for_SMI_Clustering_scored.mol2"

GRID_PREFIX="/gpfs/projects/AMS536/2026/group3/tutorial_isaac/Individual_Project/003_gridbox/grid"

TASK_LIST="${WORK_ROOT}/FMS_tasks.tsv"

STATUS_CSV="${WORK_ROOT}/FMS_status.csv"
ANALYSIS_CSV="${WORK_ROOT}/FMS_analysis_summary.csv"
ISLAND_CSV="${WORK_ROOT}/FMS_island_statistics.csv"
MEMBER_CSV="${WORK_ROOT}/FMS_member_statistics.csv"
CALCULATIONS_CSV="${WORK_ROOT}/FMS_island_calculations.csv"

SLURM_PARTITION="long-28core"
SLURM_TIME="2-00:00:00"

TASKS_PER_NODE=28
MAX_NODES=4

cutoff_label()
{
    local CUTOFF="$1"

    echo "${CUTOFF}" \
        | sed 's/-/minus_/g' \
        | sed 's/\./p/g'
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    echo
    echo "FMS Similarity Island configuration"
    echo
    echo "Workflow directory: ${WORK_ROOT}"
    echo "DOCK binary:       ${DOCK_BIN}"
    echo "Ligand file:       ${LIGAND_ATOM_FILE}"
    echo "Grid prefix:       ${GRID_PREFIX}"
    echo "Partition:         ${SLURM_PARTITION}"
    echo "Tasks per node:    ${TASKS_PER_NODE}"
    echo
    echo "FMS cutoffs:"
    printf '  %s\n' "${FMS_CUTOFFS[@]}"
    echo
fi
