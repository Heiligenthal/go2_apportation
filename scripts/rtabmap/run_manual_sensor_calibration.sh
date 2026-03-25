#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTAINER_NAME="${CONTAINER_NAME:-go2_board_runtime}"
RESTART_CONTAINER=0
PRIVILEGED=0
WITH_RVIZ=1

usage() {
  cat <<'USAGE'
Usage:
  scripts/rtabmap/run_manual_sensor_calibration.sh [options]

Options:
  --restart-container   Stop running runtime container and start fresh
  --privileged          Start/restart runtime container with ENABLE_PRIVILEGED=1
  --no-rviz             Start helper + ROS path without launching RViz
  -h, --help            Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --restart-container)
      RESTART_CONTAINER=1
      shift
      ;;
    --privileged)
      PRIVILEGED=1
      shift
      ;;
    --no-rviz)
      WITH_RVIZ=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[run_manual_sensor_calibration] ERROR: unknown argument '$1'." >&2
      usage >&2
      exit 2
      ;;
  esac
done

log() {
  printf '[run_manual_sensor_calibration] %s\n' "$*"
}

container_running() {
  docker ps --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"
}

if ! command -v docker >/dev/null 2>&1; then
  echo "[run_manual_sensor_calibration] ERROR: docker CLI not found." >&2
  exit 1
fi

if [[ ! -x "${ROOT_DIR}/scripts/bringup/run_board_runtime.sh" ]]; then
  echo "[run_manual_sensor_calibration] ERROR: scripts/bringup/run_board_runtime.sh missing or not executable." >&2
  exit 1
fi

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${ROOT_DIR}/artifacts/manual_calibration/${TIMESTAMP}"
INNER_SCRIPT_HOST="${RUN_DIR}/manual_sensor_calibration_inner.sh"
SUMMARY_LOG="${RUN_DIR}/summary.log"
mkdir -p "${RUN_DIR}"

log_file() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "${SUMMARY_LOG}"
}

if container_running && [[ "${RESTART_CONTAINER}" -eq 1 ]]; then
  log_file "Stopping running container '${CONTAINER_NAME}' (--restart-container)."
  docker stop "${CONTAINER_NAME}" >>"${RUN_DIR}/00_container_manage.out.log" 2>>"${RUN_DIR}/00_container_manage.err.log"
fi

if ! container_running; then
  log_file "Starting runtime container '${CONTAINER_NAME}' via run_board_runtime.sh --run 'sleep infinity' (privileged=${PRIVILEGED})."
  if [[ "${PRIVILEGED}" -eq 1 ]]; then
    ENABLE_PRIVILEGED=1 CONTAINER_NAME="${CONTAINER_NAME}" \
      "${ROOT_DIR}/scripts/bringup/run_board_runtime.sh" --run "sleep infinity" \
      >"${RUN_DIR}/00_runtime_start.out.log" \
      2>"${RUN_DIR}/00_runtime_start.err.log" &
  else
    CONTAINER_NAME="${CONTAINER_NAME}" \
      "${ROOT_DIR}/scripts/bringup/run_board_runtime.sh" --run "sleep infinity" \
      >"${RUN_DIR}/00_runtime_start.out.log" \
      2>"${RUN_DIR}/00_runtime_start.err.log" &
  fi
  launcher_pid=$!
  ready=0
  for _ in $(seq 1 30); do
    if container_running; then
      ready=1
      break
    fi
    if ! kill -0 "${launcher_pid}" 2>/dev/null; then
      break
    fi
    sleep 1
  done
  if [[ "${ready}" -ne 1 ]]; then
    log_file "FAIL: runtime container '${CONTAINER_NAME}' did not become ready."
    exit 1
  fi
  log_file "Runtime container '${CONTAINER_NAME}' is running."
else
  log_file "Reusing running container '${CONTAINER_NAME}'."
fi

cat >"${INNER_SCRIPT_HOST}" <<'INNER_EOF'
#!/usr/bin/env bash
set -euo pipefail

RUN_DIR="$1"
WITH_RVIZ="$2"
ROOT_DIR="/workspace/repo"
LAUNCH_PID=""

step_log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "${RUN_DIR}/summary.log"
}

source_env() {
  local restore_nounset=0
  if [[ $- == *u* ]]; then
    restore_nounset=1
    set +u
  fi
  source /opt/ros/humble/setup.bash
  if [[ -f "${ROOT_DIR}/install_container/setup.bash" ]]; then
    source "${ROOT_DIR}/install_container/setup.bash"
  elif [[ -f "${ROOT_DIR}/install/setup.bash" ]]; then
    source "${ROOT_DIR}/install/setup.bash"
  fi
  if [[ "${restore_nounset}" -eq 1 ]]; then
    set -u
  fi
}

cleanup() {
  set +e
  if [[ -n "${LAUNCH_PID}" ]] && kill -0 "${LAUNCH_PID}" 2>/dev/null; then
    kill -INT "${LAUNCH_PID}" >/dev/null 2>&1 || true
    wait "${LAUNCH_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

mkdir -p "${RUN_DIR}"
source_env

step_log "Starting manual sensor calibration launch (rviz=${WITH_RVIZ})."
ros2 launch launch/manual_sensor_calibration.launch.py rviz:="${WITH_RVIZ}" \
  >"${RUN_DIR}/01_launch.out.log" 2>"${RUN_DIR}/01_launch.err.log" &
LAUNCH_PID=$!

sleep 3
step_log "Interactive helper starts now. RViz should show Grid, TF, Robot Model, LiDAR cloud, and camera cloud when available."
step_log "Default Robot Model source: community go2_robot_sdk/urdf/go2.urdf"
step_log "LiDAR cloud expected from board runtime on /utlidar/cloud; camera cloud expected on /camera/realsense2_camera/depth/color/points"

python3 "${ROOT_DIR}/scripts/rtabmap/manual_sensor_extrinsics_helper.py" --output-dir "${RUN_DIR}"
INNER_EOF

container_run_dir="/workspace/repo/${RUN_DIR#${ROOT_DIR}/}"
docker_exec_args=(-it)
if [[ -n "${DISPLAY:-}" ]]; then
  docker_exec_args+=(-e "DISPLAY=${DISPLAY}")
fi
if [[ -n "${XAUTHORITY:-}" ]]; then
  docker_exec_args+=(-e "XAUTHORITY=${XAUTHORITY}")
fi
docker_exec_args+=(-e "QT_X11_NO_MITSHM=1")

log_file "Run dir: ${RUN_DIR}"
log_file "Starting manual sensor calibration inside container '${CONTAINER_NAME}'."
log_file "Robot Model default: community go2_robot_sdk/urdf/go2.urdf"
log_file "Productive alternative found but not used by default: repo go2_description/urdf/go2.urdf"
log_file "Reason: repo model already bakes camera_link/lidar_frame into TF, which conflicts with live manual overrides."

docker exec "${docker_exec_args[@]}" "${CONTAINER_NAME}" bash -lc \
  "cd /workspace/repo && bash ${container_run_dir}/manual_sensor_calibration_inner.sh ${container_run_dir} ${WITH_RVIZ}"
