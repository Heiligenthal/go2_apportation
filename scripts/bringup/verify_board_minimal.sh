#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ARTIFACT_ROOT="${ROOT_DIR}/artifacts/board_minimal_verify"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${ARTIFACT_ROOT}/${TIMESTAMP}"
SUMMARY_LOG="${RUN_DIR}/summary.log"

CHECK_TIMEOUT_S="${CHECK_TIMEOUT_S:-12}"
BRINGUP_WAIT_S="${BRINGUP_WAIT_S:-8}"
START_BRINGUP=0

BRINGUP_PID=""
FAILED=0

mkdir -p "${RUN_DIR}"

log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "${SUMMARY_LOG}"
}

usage() {
  cat <<'EOF'
Usage:
  scripts/bringup/verify_board_minimal.sh [--start-bringup]

Options:
  --start-bringup    Startet optional scripts/bringup/run_board_minimal.sh im Hintergrund.
  -h, --help         Zeigt diese Hilfe.

Env:
  CHECK_TIMEOUT_S    Timeout pro Check (Default: 12)
  BRINGUP_WAIT_S     Wartezeit nach optionalem Bringup-Start (Default: 8)
EOF
}

cleanup() {
  if [[ -n "${BRINGUP_PID}" ]] && kill -0 "${BRINGUP_PID}" >/dev/null 2>&1; then
    log "Stopping optional bringup process (pid=${BRINGUP_PID})"
    kill "${BRINGUP_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

while [[ $# -gt 0 ]]; do
  case "$1" in
    --start-bringup)
      START_BRINGUP=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v ros2 >/dev/null 2>&1; then
  echo "[ERROR] ros2 CLI not found in PATH." >&2
  exit 1
fi

extract_launch_default() {
  local arg_name="$1"
  local launch_file="${ROOT_DIR}/launch/board_minimal.launch.py"
  sed -n "s/.*DeclareLaunchArgument(\"${arg_name}\", default_value=\"\\([^\"]*\\)\".*/\\1/p" "${launch_file}" | head -n 1
}

extract_rtabmap_frame() {
  local key="$1"
  local cfg="${ROOT_DIR}/config/rtabmap_params.yaml"
  sed -n "s/^[[:space:]]*${key}:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p" "${cfg}" | head -n 1
}

PARENT_FRAME="$(extract_launch_default "parent_frame")"
CHILD_FRAME="$(extract_launch_default "child_frame")"

if [[ -z "${PARENT_FRAME}" ]]; then
  PARENT_FRAME="$(extract_rtabmap_frame "odom_frame_id")"
fi
if [[ -z "${CHILD_FRAME}" ]]; then
  CHILD_FRAME="$(extract_rtabmap_frame "base_frame_id")"
fi

if [[ -z "${PARENT_FRAME}" ]]; then
  PARENT_FRAME="odom"
  log "Frame fallback used for parent_frame=odom (could not derive from repo launch/config)."
fi
if [[ -z "${CHILD_FRAME}" ]]; then
  CHILD_FRAME="base_link"
  log "Frame fallback used for child_frame=base_link (could not derive from repo launch/config)."
fi

run_check() {
  local check_id="$1"
  shift
  local logfile="${RUN_DIR}/${check_id}.log"

  set +e
  timeout "${CHECK_TIMEOUT_S}s" "$@" >"${logfile}" 2>&1
  local rc=$?
  set -e

  if [[ ${rc} -eq 0 ]]; then
    log "PASS ${check_id}"
  else
    log "FAIL ${check_id} (rc=${rc})"
    FAILED=1
  fi
  return 0
}

if [[ ${START_BRINGUP} -eq 1 ]]; then
  log "Starting optional bringup via scripts/bringup/run_board_minimal.sh"
  if command -v script >/dev/null 2>&1; then
    script -q -c "bash ${ROOT_DIR}/scripts/bringup/run_board_minimal.sh" "${RUN_DIR}/bringup.session.log" >/dev/null 2>&1 &
  else
    bash "${ROOT_DIR}/scripts/bringup/run_board_minimal.sh" >"${RUN_DIR}/bringup.log" 2>&1 &
  fi
  BRINGUP_PID="$!"
  sleep "${BRINGUP_WAIT_S}"
  if ! kill -0 "${BRINGUP_PID}" >/dev/null 2>&1; then
    log "Bringup process exited early. See bringup log artifacts."
    FAILED=1
  fi
fi

log "Artifacts directory: ${RUN_DIR}"
log "Using TF frame check: ${PARENT_FRAME} -> ${CHILD_FRAME}"

run_check "topic_list" ros2 topic list

TOPIC_LIST_FILE="${RUN_DIR}/topic_list.log"
ODOM_TOPIC="/utlidar/robot_odom"

if grep -qx "${ODOM_TOPIC}" "${TOPIC_LIST_FILE}" 2>/dev/null; then
  log "Using odom topic: ${ODOM_TOPIC} (exact match found)"
else
  auto_topic="$(grep -E '/.*odom' "${TOPIC_LIST_FILE}" 2>/dev/null | head -n 1 || true)"
  if [[ -n "${auto_topic}" ]]; then
    ODOM_TOPIC="${auto_topic}"
    log "Using odom topic: ${ODOM_TOPIC} (auto-detected from topic list)"
  else
    ODOM_TOPIC=""
    log "No odom-like topic found in topic list; skipping odom echo check."
    FAILED=1
  fi
fi

if [[ -n "${ODOM_TOPIC}" ]]; then
  run_check "odom_echo_once" ros2 topic echo -n 1 "${ODOM_TOPIC}"
fi

run_check "tf2_echo_${PARENT_FRAME}_to_${CHILD_FRAME}" ros2 run tf2_ros tf2_echo "${PARENT_FRAME}" "${CHILD_FRAME}"

if [[ ${FAILED} -eq 0 ]]; then
  log "VERIFY RESULT: PASS"
else
  log "VERIFY RESULT: FAIL (see logs in ${RUN_DIR})"
fi

exit "${FAILED}"
