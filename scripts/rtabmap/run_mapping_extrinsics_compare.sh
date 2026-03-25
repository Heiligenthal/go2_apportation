#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MAPPING_RUNNER="${ROOT_DIR}/scripts/rtabmap/run_r3_mapping_e2e.sh"
EVAL_HELPER="${ROOT_DIR}/scripts/rtabmap/evaluate_map_artifacts.py"
COMPARE_TS="$(date +%Y%m%d_%H%M%S)"
COMPARE_DIR="${ROOT_DIR}/artifacts/mapping_compare/${COMPARE_TS}"
SUMMARY_FILE="${COMPARE_DIR}/comparison_summary.txt"
DURATION_SECONDS=180
PRIVILEGED=0
BASELINE_EXTRA_ARGS=()
TEST_EXTRA_ARGS=()

usage() {
  cat <<'USAGE'
Usage:
  scripts/rtabmap/run_mapping_extrinsics_compare.sh [options]

Options:
  --duration-seconds <N>   Mapping duration for both runs (default: 180)
  --privileged             Pass --privileged to both mapping runs
  --baseline-extra "<...>" Extra args appended to the baseline run
  --test-extra "<...>"     Extra args appended to the test-extrinsics run
  -h, --help               Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --duration-seconds)
      [[ $# -lt 2 ]] && { echo "[mapping_compare] ERROR: --duration-seconds requires a value." >&2; exit 2; }
      DURATION_SECONDS="$2"
      shift 2
      ;;
    --privileged)
      PRIVILEGED=1
      shift
      ;;
    --baseline-extra)
      [[ $# -lt 2 ]] && { echo "[mapping_compare] ERROR: --baseline-extra requires a value." >&2; exit 2; }
      # shellcheck disable=SC2206
      BASELINE_EXTRA_ARGS=($2)
      shift 2
      ;;
    --test-extra)
      [[ $# -lt 2 ]] && { echo "[mapping_compare] ERROR: --test-extra requires a value." >&2; exit 2; }
      # shellcheck disable=SC2206
      TEST_EXTRA_ARGS=($2)
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[mapping_compare] ERROR: unknown argument '$1'." >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! -x "${MAPPING_RUNNER}" ]]; then
  echo "[mapping_compare] ERROR: missing executable ${MAPPING_RUNNER}." >&2
  exit 1
fi

if [[ ! -f "${EVAL_HELPER}" ]]; then
  echo "[mapping_compare] ERROR: missing ${EVAL_HELPER}." >&2
  exit 1
fi

mkdir -p "${COMPARE_DIR}"

log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "${SUMMARY_FILE}" >&2
}

latest_dir() {
  local base_dir="$1"
  ls -1dt "${base_dir}"/* 2>/dev/null | head -n 1 || true
}

run_and_capture_latest() {
  local label="$1"
  shift
  local before_map before_run after_map after_run
  before_map="$(latest_dir "${ROOT_DIR}/artifacts/maps")"
  before_run="$(latest_dir "${ROOT_DIR}/artifacts/r3_mapping")"

  log "Starting ${label} mapping run."
  "$@" | tee -a "${SUMMARY_FILE}" >&2

  after_map="$(latest_dir "${ROOT_DIR}/artifacts/maps")"
  after_run="$(latest_dir "${ROOT_DIR}/artifacts/r3_mapping")"

  if [[ -z "${after_map}" || -z "${after_run}" ]]; then
    echo "[mapping_compare] ERROR: could not resolve latest artifact directories after ${label} run." >&2
    exit 1
  fi

  if [[ "${after_map}" == "${before_map}" ]]; then
    log "WARN: latest map directory did not change during ${label} run."
  fi
  if [[ "${after_run}" == "${before_run}" ]]; then
    log "WARN: latest r3_mapping directory did not change during ${label} run."
  fi

  printf '%s\n%s\n' "${after_map}" "${after_run}"
}

COMMON_ARGS=(--duration-seconds "${DURATION_SECONDS}")
if [[ "${PRIVILEGED}" -eq 1 ]]; then
  COMMON_ARGS+=(--privileged)
fi

{
  log "Compare dir: ${COMPARE_DIR}"
  log "Baseline run uses current repo defaults plus --allow-uncalibrated-lidar."
  log "Test run uses --use-test-extrinsics from config/mapping_test_extrinsics.env."
} >/dev/null

mapfile -t baseline_paths < <(
  run_and_capture_latest \
    "baseline" \
    "${MAPPING_RUNNER}" "${COMMON_ARGS[@]}" --allow-uncalibrated-lidar "${BASELINE_EXTRA_ARGS[@]}"
)
BASELINE_MAP_DIR="${baseline_paths[0]}"
BASELINE_RUN_DIR="${baseline_paths[1]}"

mapfile -t test_paths < <(
  run_and_capture_latest \
    "test-extrinsics" \
    "${MAPPING_RUNNER}" "${COMMON_ARGS[@]}" --use-test-extrinsics "${TEST_EXTRA_ARGS[@]}"
)
TEST_MAP_DIR="${test_paths[0]}"
TEST_RUN_DIR="${test_paths[1]}"

log "Baseline map dir: ${BASELINE_MAP_DIR}"
log "Baseline run dir: ${BASELINE_RUN_DIR}"
log "Test map dir: ${TEST_MAP_DIR}"
log "Test run dir: ${TEST_RUN_DIR}"

python3 "${EVAL_HELPER}" \
  --map-dir "${TEST_MAP_DIR}" \
  --run-dir "${TEST_RUN_DIR}" \
  --compare-map-dir "${BASELINE_MAP_DIR}" \
  --compare-run-dir "${BASELINE_RUN_DIR}" \
  >"${COMPARE_DIR}/evaluation.txt"

{
  echo "baseline_map_dir=${BASELINE_MAP_DIR}"
  echo "baseline_run_dir=${BASELINE_RUN_DIR}"
  echo "test_map_dir=${TEST_MAP_DIR}"
  echo "test_run_dir=${TEST_RUN_DIR}"
  sed -n '1,120p' "${COMPARE_DIR}/evaluation.txt"
} >>"${SUMMARY_FILE}"

comparison_result="$(awk -F= '/^comparison_result=/{print $2; exit}' "${COMPARE_DIR}/evaluation.txt")"
baseline_warn="$(awk -F= '/^compare_tf_or_time_warning_hits=/{print $2; exit}' "${COMPARE_DIR}/evaluation.txt")"
test_warn="$(awk -F= '/^tf_or_time_warning_hits=/{print $2; exit}' "${COMPARE_DIR}/evaluation.txt")"
baseline_size="$(awk -F= '/^compare_map_pgm_size_bytes=/{print $2; exit}' "${COMPARE_DIR}/evaluation.txt")"
test_size="$(awk -F= '/^map_pgm_size_bytes=/{print $2; exit}' "${COMPARE_DIR}/evaluation.txt")"

log "Comparison result: ${comparison_result:-unknown}"
log "PGM size bytes: baseline=${baseline_size:-unknown} test=${test_size:-unknown}"
log "TF/timestamp warning hits: baseline=${baseline_warn:-unknown} test=${test_warn:-unknown}"
log "Detailed evaluation: ${COMPARE_DIR}/evaluation.txt"
log "Summary: ${SUMMARY_FILE}"
