#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${SCRIPT_DIR}/000.config.sh"

ERRORS=0

check_file()
{
    local NAME="$1"
    local FILE="$2"

    if [[ ! -f "${FILE}" ]]; then
        echo "ERROR: Missing ${NAME}: ${FILE}"
        ERRORS=$((ERRORS + 1))
    fi
}

check_executable()
{
    local NAME="$1"
    local FILE="$2"

    if [[ ! -x "${FILE}" ]]; then
        echo "ERROR: Missing executable ${NAME}: ${FILE}"
        ERRORS=$((ERRORS + 1))
    fi
}

echo
echo "Validating FMS workflow inputs..."
echo

check_executable "DOCK6" "${DOCK_BIN}"
check_file "ligand MOL2" "${LIGAND_ATOM_FILE}"
check_file "grid energy file" "${GRID_PREFIX}.nrg"
check_file "grid bitmap file" "${GRID_PREFIX}.bmp"
check_file "VDW definition" "${VDW_DEFN_FILE}"
check_file "flex definition" "${FLEX_DEFN_FILE}"
check_file "pharmacophore definition" "${PH4_DEFN_FILE}"

if (( ERRORS > 0 )); then
    echo
    echo "ERROR: ${ERRORS} required input(s) are missing."
    exit 1
fi

echo "Validation passed."
echo
echo "Generating FMS input files..."
echo

for CUTOFF in "${FMS_CUTOFFS[@]}"; do
    LABEL="$(cutoff_label "${CUTOFF}")"
    CASE_NAME="FMS_Island_${LABEL}"

    INPUT_FILE="${WORK_ROOT}/${CASE_NAME}.in"
    SUMMARY_FILE="${WORK_ROOT}/${CASE_NAME}_summary.out"

    cat > "${INPUT_FILE}" << EOF_IN
conformer_search_type                                      analysis
ligand_atom_file                                           ${LIGAND_ATOM_FILE}
limit_max_ligands                                          no
skip_molecule                                              no
read_mol_solvation                                         no
calculate_rmsd                                             no
cluster_by_similarity_island                               yes
similarity_island_scoring_type                             fms
similarity_island_fms_cutoff                               ${CUTOFF}
similarity_island_retention_mode                           all
similarity_island_write_summary                            yes
similarity_island_summary_file                             ${SUMMARY_FILE}
score_molecules                                            yes
contact_score_primary                                      no
grid_score_primary                                         no
gist_score_primary                                         no
multigrid_score_primary                                    no
dock3.5_score_primary                                      no
continuous_score_primary                                   no
footprint_similarity_score_primary                         no
pharmacophore_score_primary                                no
hbond_score_primary                                        no
internal_energy_score_primary                              no
descriptor_score_primary                                   yes
descriptor_use_grid_score                                  yes
descriptor_use_grid_lig_efficiency                         no
descriptor_use_pharmacophore_score                         no
descriptor_use_tanimoto                                    no
descriptor_use_hungarian                                   no
descriptor_use_volume_overlap                              no
descriptor_use_gist                                        no
descriptor_use_dock3.5                                     no
descriptor_grid_score_rep_rad_scale                        1
descriptor_grid_score_vdw_scale                            1
descriptor_grid_score_es_scale                             1
descriptor_grid_score_grid_prefix                          ${GRID_PREFIX}
descriptor_weight_grid_score                               1
atom_model                                                 all
vdw_defn_file                                              ${VDW_DEFN_FILE}
flex_defn_file                                             ${FLEX_DEFN_FILE}
pharmacophore_defn_file                                    ${PH4_DEFN_FILE}
ligand_outfile_prefix                                      ${WORK_ROOT}/${CASE_NAME}
EOF_IN

    echo "${CASE_NAME}.in"
done

echo
echo "Generated ${#FMS_CUTOFFS[@]} FMS input files."
echo
