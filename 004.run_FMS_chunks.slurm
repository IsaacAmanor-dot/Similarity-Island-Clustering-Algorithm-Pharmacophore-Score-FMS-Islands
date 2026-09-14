#!/bin/bash

#SBATCH --job-name=FMS_Islands
#SBATCH --partition=long-28core
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=28
#SBATCH --time=2-00:00:00
#SBATCH --output=FMS_slurm_%A_%a.out

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${SCRIPT_DIR}/000.config.sh"

if [[ ! -s "${TASK_LIST}" ]]; then
    echo "ERROR: Missing task list: ${TASK_LIST}"
    echo "Run 002.make_task_list.sh first."
    exit 1
fi

TOTAL_TASKS=$(awk 'NR > 1 {count++} END {print count+0}' "${TASK_LIST}")

if (( TOTAL_TASKS == 0 )); then
    echo "ERROR: No FMS tasks found."
    exit 1
fi

ARRAY_TASK_ID="${SLURM_ARRAY_TASK_ID:-1}"

START_TASK=$(( (ARRAY_TASK_ID - 1) * TASKS_PER_NODE + 1 ))
END_TASK=$(( START_TASK + TASKS_PER_NODE - 1 ))

if (( START_TASK > TOTAL_TASKS )); then
    echo "ERROR: Chunk ${ARRAY_TASK_ID} begins beyond the task list."
    echo "Total tasks: ${TOTAL_TASKS}"
    exit 1
fi

if (( END_TASK > TOTAL_TASKS )); then
    END_TASK=${TOTAL_TASKS}
fi

echo
echo "FMS Similarity Island chunk"
echo
echo "Array ID:    ${ARRAY_TASK_ID}"
echo "Total tasks: ${TOTAL_TASKS}"
echo "Task range:  ${START_TASK}-${END_TASK}"
echo "Node:        $(hostname)"
echo "Started:     $(date)"
echo

PIDS=()
TASK_IDS=()

for (( TASK_ID=START_TASK; TASK_ID<=END_TASK; TASK_ID++ )); do
    echo "Launching task ${TASK_ID}"

    bash "${SCRIPT_DIR}/003.run_one_task.slurm" "${TASK_ID}" &

    PIDS+=("$!")
    TASK_IDS+=("${TASK_ID}")
done

FAILURES=0

for INDEX in "${!PIDS[@]}"; do
    PID="${PIDS[$INDEX]}"
    TASK_ID="${TASK_IDS[$INDEX]}"

    if wait "${PID}"; then
        echo "Task ${TASK_ID}: complete"
    else
        echo "Task ${TASK_ID}: failed"
        FAILURES=$((FAILURES + 1))
    fi
done

echo
echo "Chunk finished: $(date)"
echo "Tasks launched: ${#TASK_IDS[@]}"
echo "Failures:       ${FAILURES}"
echo

if (( FAILURES > 0 )); then
    exit 1
fi

exit 0
