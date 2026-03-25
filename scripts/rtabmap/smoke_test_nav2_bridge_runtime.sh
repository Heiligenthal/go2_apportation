#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTAINER_NAME="${CONTAINER_NAME:-go2_board_runtime}"
RUN_DIR=""
TIMEOUT_SEC=20

usage() {
  cat <<'USAGE'
Usage:
  scripts/rtabmap/smoke_test_nav2_bridge_runtime.sh [options]

Options:
  --run-dir <path>      Explicit artifacts/nav2_bridge/<timestamp> directory to inspect
  --timeout <seconds>   Timeout for runtime checks (default: 20)
  -h, --help            Show this help

This script validates the real productive runtime path:
  board_description + realsense_board + rtabmap_localization + nav2_rtabmap + go2_nav2_bridge

Checks:
  1) /go2_nav2_bridge node visible
  2) base_link -> base_link_nav2 TF resolvable
  3) /cmd_vel_nav2 type and bridge subscription visible
  4) /look_yaw_delta, /balance_rpy_cmd, /control_mode_cmd wired to the bridge
  5) legacy /odom_nav2 is not active by default
  6) watchdog produces a StopMove timeout warning after a zero-twist test publish
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-dir)
      [[ $# -lt 2 ]] && { echo "ERROR: --run-dir requires value" >&2; exit 2; }
      RUN_DIR="$2"
      shift 2
      ;;
    --timeout)
      [[ $# -lt 2 ]] && { echo "ERROR: --timeout requires value" >&2; exit 2; }
      TIMEOUT_SEC="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument '$1'" >&2
      usage >&2
      exit 2
      ;;
  esac
done

log() {
  echo "[smoke_test_nav2_bridge_runtime] $*"
}

if [[ -z "${RUN_DIR}" ]]; then
  RUN_DIR="$(ls -1d "${ROOT_DIR}/artifacts/nav2_bridge"/* 2>/dev/null | sort | tail -n 1 || true)"
fi

if [[ -z "${RUN_DIR}" || ! -d "${RUN_DIR}" ]]; then
  log "ERROR: no nav2_bridge run directory found. Start the stack first with run_nav2_bridge_with_rtabmap_localization.sh."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  log "ERROR: docker CLI not found."
  exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"; then
  log "ERROR: container '${CONTAINER_NAME}' is not running."
  exit 1
fi

RUNTIME_LOG="${RUN_DIR}/06_nav2_bridge.out.log"
if [[ ! -f "${RUNTIME_LOG}" ]]; then
  log "ERROR: expected runtime log missing: ${RUNTIME_LOG}"
  exit 1
fi

INNER_SCRIPT="${RUN_DIR}/bridge_runtime_smoke_inner.sh"
cat >"${INNER_SCRIPT}" <<'INNER_EOF'
#!/usr/bin/env bash
set -euo pipefail

TIMEOUT_SEC="$1"

source /opt/ros/humble/setup.bash
if [[ -f /workspace/repo/install_container/setup.bash ]]; then
  source /workspace/repo/install_container/setup.bash
elif [[ -f /workspace/repo/install/setup.bash ]]; then
  source /workspace/repo/install/setup.bash
fi

wait_node_visible() {
  local node_name="$1"
  local timeout_sec="$2"
  local start_ts="$(date +%s)"
  while true; do
    if ros2 node list | grep -Fxq "${node_name}"; then
      return 0
    fi
    if (( $(date +%s) - start_ts >= timeout_sec )); then
      return 1
    fi
    sleep 1
  done
}

wait_topic_info_has_node() {
  local topic="$1"
  local node_name="$2"
  local timeout_sec="$3"
  local start_ts="$(date +%s)"
  while true; do
    if ros2 topic info "${topic}" -v >"/tmp/$(basename "${topic}").info.log" 2>/dev/null && \
      grep -Eq "Node name:[[:space:]]*${node_name}$|Node name:[[:space:]]*/${node_name}$" "/tmp/$(basename "${topic}").info.log"; then
      return 0
    fi
    if (( $(date +%s) - start_ts >= timeout_sec )); then
      return 1
    fi
    sleep 1
  done
}

wait_tf() {
  local parent="$1"
  local child="$2"
  local timeout_sec="$3"
  local start_ts="$(date +%s)"
  while true; do
    if timeout 3s ros2 run tf2_ros tf2_echo "${parent}" "${child}" >/tmp/tf_smoke.out 2>/tmp/tf_smoke.err; then
      return 0
    fi
    if grep -Eq "At time|Translation:|Rotation:" /tmp/tf_smoke.out 2>/dev/null; then
      return 0
    fi
    if (( $(date +%s) - start_ts >= timeout_sec )); then
      return 1
    fi
    sleep 1
  done
}

wait_node_visible "/go2_nav2_bridge" "${TIMEOUT_SEC}"
ros2 topic type /cmd_vel_nav2 >/tmp/cmd_vel_nav2_type.out
wait_topic_info_has_node "/cmd_vel_nav2" "go2_nav2_bridge" "${TIMEOUT_SEC}"
wait_topic_info_has_node "/look_yaw_delta" "go2_nav2_bridge" "${TIMEOUT_SEC}"
wait_topic_info_has_node "/balance_rpy_cmd" "go2_nav2_bridge" "${TIMEOUT_SEC}"
wait_topic_info_has_node "/control_mode_cmd" "go2_nav2_bridge" "${TIMEOUT_SEC}"
wait_tf "base_link" "base_link_nav2" "${TIMEOUT_SEC}"

if ros2 topic info /odom_nav2 -v >/tmp/odom_nav2_info.out 2>/tmp/odom_nav2_info.err; then
  if grep -Eq "Publisher count:[[:space:]]*[1-9]" /tmp/odom_nav2_info.out; then
    echo "LEGACY_ODOM_ACTIVE"
    exit 20
  fi
fi

ros2 topic pub --once /cmd_vel_nav2 geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" >/tmp/cmd_vel_nav2_pub.out 2>/tmp/cmd_vel_nav2_pub.err
echo "SMOKE_OK"
INNER_EOF

chmod +x "${INNER_SCRIPT}"

log "Using run dir: ${RUN_DIR}"
log "Executing runtime smoke checks inside container '${CONTAINER_NAME}'"

BEFORE_LINES="$(wc -l < "${RUNTIME_LOG}")"
set +e
docker exec "${CONTAINER_NAME}" bash -lc "/workspace/repo/${INNER_SCRIPT#${ROOT_DIR}/} '${TIMEOUT_SEC}'" \
  >"${RUN_DIR}/08_bridge_smoke.out.log" \
  2>"${RUN_DIR}/08_bridge_smoke.err.log"
RC=$?
set -e

if [[ "${RC}" -eq 20 ]]; then
  log "FAIL: legacy /odom_nav2 has an active publisher. Productive path should not require it."
  exit 1
fi
if [[ "${RC}" -ne 0 ]]; then
  log "FAIL: container smoke checks failed. See ${RUN_DIR}/08_bridge_smoke.out.log and ${RUN_DIR}/08_bridge_smoke.err.log"
  exit "${RC}"
fi

sleep 1
tail -n +"$((BEFORE_LINES + 1))" "${RUNTIME_LOG}" >"${RUN_DIR}/08_bridge_smoke_log_delta.out.log" || true
if ! grep -q "cmd_vel_nav2 stream is fresh again" "${RUN_DIR}/08_bridge_smoke_log_delta.out.log"; then
  log "FAIL: bridge log did not show fresh /cmd_vel_nav2 handling after zero-twist smoke publish."
  exit 1
fi
if ! grep -q "watchdog expired" "${RUN_DIR}/08_bridge_smoke_log_delta.out.log"; then
  log "FAIL: bridge log did not show watchdog stop after the zero-twist smoke publish."
  exit 1
fi

log "PASS: bridge node visible, base_link->base_link_nav2 TF resolvable, productive topics wired, legacy odom inactive, watchdog stop observed."
