#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${SCRIPT_DIR}/000.config.sh"

if [[ -z "${SLURM_ARRAY_TASK_ID:-}" ]]; then
    echo "ERROR: SLURM_ARRAY_TASK_ID is not set."
    exit 1
fi

TOTAL_TASKS=$(awk 'NR > 1 {n++} END {print n+0}' "${TASK_LIST}")

START_TASK=$(
    (SLURM_ARRAY_TASK_ID - 1) * TASKS_PER_NODE + 1
)

END_TASK=$(
    START_TASK + TASKS_PER_NODE - 1
)

if (( END_TASK > TOTAL_TASKS )); then
    END_TASK=${TOTAL_TASKS}
fi

echo
echo "FMS chunk"
echo
echo "Array ID:   ${SLURM_ARRAY_TASK_ID}"
echo "Task range: ${START_TASK}-${END_TASK}"
echo "Node:       $(hostname)"
echo "Started:    $(date)"
echo

PIDS=()
TASK_IDS=()

for TASK_ID in $(seq "${START_TASK}" "${END_TASK}"); do
    bash "${SCRIPT_DIR}/003.run_one_task.slurm" "${TASK_ID}" &

    PIDS+=("$!")
    TASK_IDS+=("${TASK_ID}")
done

FAILURES=0

for INDEX in "${!PIDS[@]}"; do
    PID="${PIDS[$INDEX]}"
    TASK_ID="${TASK_IDS[$INDEX]}"

    if ! wait "${PID}"; then
        echo "Task ${TASK_ID} failed."
        FAILURES=$((FAILURES + 1))
    fi
done

echo
echo "Chunk finished: $(date)"
echo "Failures: ${FAILURES}"
echo

if (( FAILURES > 0 )); then
    exit 1
fi
