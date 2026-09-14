#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${SCRIPT_DIR}/000.config.sh"

if [[ ! -s "${TASK_LIST}" ]]; then
    echo "ERROR: Missing task list: ${TASK_LIST}"
    echo "Run 002.make_task_list.sh first."
    exit 1
fi

N_TASKS=$(awk 'NR > 1 {n++} END {print n+0}' "${TASK_LIST}")

if (( N_TASKS == 0 )); then
    echo "ERROR: Task list contains no tasks."
    exit 1
fi

N_CHUNKS=$(
    (N_TASKS + TASKS_PER_NODE - 1) / TASKS_PER_NODE
)

if (( N_TASKS < TASKS_PER_NODE )); then
    CPUS_REQUESTED=${N_TASKS}
else
    CPUS_REQUESTED=${TASKS_PER_NODE}
fi

if (( MAX_NODES < N_CHUNKS )); then
    ARRAY_SPEC="1-${N_CHUNKS}%${MAX_NODES}"
else
    ARRAY_SPEC="1-${N_CHUNKS}"
fi

echo
echo "Submitting FMS Similarity Island experiment"
echo
echo "FMS calculations: ${N_TASKS}"
echo "Chunks:           ${N_CHUNKS}"
echo "CPUs per chunk:   ${CPUS_REQUESTED}"
echo "Array:            ${ARRAY_SPEC}"
echo "Partition:        ${SLURM_PARTITION}"
echo "Walltime:         ${SLURM_TIME}"
echo

sbatch \
    --job-name=FMS_Islands \
    --partition="${SLURM_PARTITION}" \
    --nodes=1 \
    --ntasks=1 \
    --cpus-per-task="${CPUS_REQUESTED}" \
    --time="${SLURM_TIME}" \
    --array="${ARRAY_SPEC}" \
    --output="${WORK_ROOT}/FMS_slurm_%A_%a.out" \
    "${SCRIPT_DIR}/004.run_FMS_chunks.slurm"
