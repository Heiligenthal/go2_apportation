#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYDEPS_DIR="${REPO_ROOT}/.pydeps/camera_mount"
REQUIREMENTS_FILE="${REPO_ROOT}/scripts/rtabmap/requirements_camera_mount.txt"
PYTHONPATH_WITH_PYDEPS="${PYDEPS_DIR}${PYTHONPATH:+:${PYTHONPATH}}"

log() {
  printf '[ensure_camera_mount_python_env] %s\n' "$*"
}

die() {
  printf '[ensure_camera_mount_python_env] ERROR: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage:
  scripts/rtabmap/ensure_camera_mount_python_env.sh [--mode dry-run|calibrate]

Modes:
  dry-run     Ensure imports needed for bag selection, bootstrap and dry-run checks
  calibrate   Ensure imports needed for the full calibration and replay/map scoring path
USAGE
}

required_imports_for_mode() {
  local mode="$1"
  case "${mode}" in
    dry-run)
      printf '%s\n' numpy scipy yaml
      ;;
    calibrate)
      printf '%s\n' numpy scipy yaml optuna cv2
      ;;
    *)
      die "Unsupported mode '${mode}'. Use dry-run or calibrate."
      ;;
  esac
}

check_imports() {
  local mode="$1"
  local report_file="$2"
  local pythonpath_value="${3:-}"
  PYTHONPATH="${pythonpath_value}" python3 - "$mode" >"${report_file}" <<'PY'
import importlib
import sys

mode = sys.argv[1]
required = {
    "dry-run": ["numpy", "scipy", "yaml"],
    "calibrate": ["numpy", "scipy", "yaml", "optuna", "cv2"],
}[mode]

for module_name in required:
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "n/a")
        print(f"{module_name}|OK|{version}")
    except Exception as exc:
        print(f"{module_name}|FAIL|{exc!r}")
PY
}

module_patterns() {
  local module_name="$1"
  case "${module_name}" in
    numpy)
      printf '%s\n' "numpy" "numpy-*.dist-info" "numpy.libs"
      ;;
    scipy)
      printf '%s\n' "scipy" "scipy-*.dist-info" "scipy.libs"
      ;;
    yaml)
      printf '%s\n' "yaml" "PyYAML-*.dist-info" "_yaml*"
      ;;
    optuna)
      printf '%s\n' "optuna" "optuna-*.dist-info"
      ;;
    cv2)
      printf '%s\n' "cv2" "opencv_python*.dist-info" "opencv_python.libs"
      ;;
  esac
}

purge_pydeps_module() {
  local module_name="$1"
  local pattern target
  while IFS= read -r pattern; do
    [[ -n "${pattern}" ]] || continue
    for target in "${PYDEPS_DIR}"/${pattern}; do
      [[ -e "${target}" ]] || continue
      rm -rf "${target}"
      log "Removed broken repo-local pydeps entry: ${target}"
    done
  done < <(module_patterns "${module_name}")
}

read_report() {
  local report_file="$1"
  declare -n out_ref="$2"
  local line module_name status detail
  while IFS='|' read -r module_name status detail; do
    [[ -n "${module_name}" ]] || continue
    out_ref["${module_name}"]="${status}|${detail}"
  done <"${report_file}"
}

main() {
  local mode="calibrate"
  local system_report combined_report
  local -A system_status=()
  local -A combined_status=()
  local -a missing_imports=()
  local -a present_imports=()
  local module_name system_entry combined_entry

  while (($#)); do
    case "$1" in
      --mode)
        shift || die "Missing value after --mode"
        mode="$1"
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "Unknown argument '$1'"
        ;;
    esac
    shift || true
  done

  [[ -f "${REQUIREMENTS_FILE}" ]] || die "Requirements file not found: ${REQUIREMENTS_FILE}"
  mkdir -p "${REPO_ROOT}/.pydeps" "${PYDEPS_DIR}"
  system_report="$(mktemp)"
  combined_report="$(mktemp)"
  trap "rm -f '${system_report}' '${combined_report}'" EXIT

  log "Using persistent repo-local pydeps dir at ${PYDEPS_DIR}"
  log "Runtime check mode: ${mode}"
  log "Expected camera-mount imports: $(required_imports_for_mode "${mode}" | tr '\n' ' ' | sed 's/[[:space:]]*$//')"

  check_imports "${mode}" "${system_report}" "${PYTHONPATH:-}"
  check_imports "${mode}" "${combined_report}" "${PYTHONPATH_WITH_PYDEPS}"
  read_report "${system_report}" system_status
  read_report "${combined_report}" combined_status

  while IFS= read -r module_name; do
    system_entry="${system_status[${module_name}]:-FAIL|unknown}"
    combined_entry="${combined_status[${module_name}]:-FAIL|unknown}"

    if [[ "${combined_entry%%|*}" == "FAIL" && "${system_entry%%|*}" == "OK" ]]; then
      log "Repo-local pydeps are shadowing a working system import for ${module_name}; cleaning local leftovers."
      purge_pydeps_module "${module_name}"
    fi
  done < <(required_imports_for_mode "${mode}")

  check_imports "${mode}" "${combined_report}" "${PYTHONPATH_WITH_PYDEPS}"
  combined_status=()
  read_report "${combined_report}" combined_status

  while IFS= read -r module_name; do
    combined_entry="${combined_status[${module_name}]:-FAIL|unknown}"
    if [[ "${combined_entry%%|*}" == "OK" ]]; then
      present_imports+=("${module_name}")
    else
      missing_imports+=("${module_name}")
      log "Missing/broken import: ${module_name} (${combined_entry#*|})"
    fi
  done < <(required_imports_for_mode "${mode}")

  if ((${#present_imports[@]} > 0)); then
    log "Already importable in runtime + repo-local pydeps: ${present_imports[*]}"
  fi

  if ((${#missing_imports[@]} == 0)); then
    log "All required camera-mount imports for mode '${mode}' are already available; no installation needed."
  else
    log "Installing/refreshing repo-local camera-mount Python requirements from ${REQUIREMENTS_FILE}"
    if ! python3 -m pip install --upgrade --target "${PYDEPS_DIR}" -r "${REQUIREMENTS_FILE}"; then
      die "pip installation into ${PYDEPS_DIR} failed. Check network/index access or provide the required wheels in the runtime environment."
    fi

    check_imports "${mode}" "${combined_report}" "${PYTHONPATH_WITH_PYDEPS}"
    combined_status=()
    read_report "${combined_report}" combined_status
    missing_imports=()
    while IFS= read -r module_name; do
      combined_entry="${combined_status[${module_name}]:-FAIL|unknown}"
      if [[ "${combined_entry%%|*}" != "OK" ]]; then
        missing_imports+=("${module_name}")
        log "Still failing after install: ${module_name} (${combined_entry#*|})"
      fi
    done < <(required_imports_for_mode "${mode}")
    ((${#missing_imports[@]} == 0)) \
      || die "Required camera-mount imports for mode '${mode}' are still missing after install: ${missing_imports[*]}"
    log "Repo-local camera-mount Python requirements are ready."
  fi

  log "Python executable: $(command -v python3)"
  log "PYTHONPATH addition: ${PYDEPS_DIR}"
}

main "$@"
