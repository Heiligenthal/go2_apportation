#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTAINER_NAME="${CONTAINER_NAME:-go2_board_runtime}"
RESTART_CONTAINER=0
PRIVILEGED=0
WITH_RVIZ=0

usage() {
  cat <<'USAGE'
Usage:
  scripts/rtabmap/run_manual_sensor_calibration.sh [options]

Options:
  --restart-container   Stop running runtime container and start fresh
  --privileged          Start/restart runtime container with ENABLE_PRIVILEGED=1
  --with-container-rviz Debug only: also start RViz inside the runtime container
  --no-rviz             Deprecated no-op; board-side default is already without RViz
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
    --with-container-rviz)
      WITH_RVIZ=1
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
RVIZ_PID=""
CAMERA_THROTTLE_PID=""
LIDAR_THROTTLE_PID=""
CAMERA_RGB_TOPIC=""
CAMERA_DEPTH_TOPIC=""
CAMERA_DEPTH_TOPIC_MODE=""
CAMERA_INFO_TOPIC=""
CAMERA_POINTCLOUD_TOPIC=""
LIDAR_CLOUD_TOPIC=""
RVIZ_CAMERA_TOPIC="/manual_calibration/camera_cloud"
RVIZ_LIDAR_TOPIC="/manual_calibration/lidar_cloud"

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
  if [[ -n "${CAMERA_THROTTLE_PID}" ]] && kill -0 "${CAMERA_THROTTLE_PID}" 2>/dev/null; then
    kill -INT "${CAMERA_THROTTLE_PID}" >/dev/null 2>&1 || true
    wait "${CAMERA_THROTTLE_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${LIDAR_THROTTLE_PID}" ]] && kill -0 "${LIDAR_THROTTLE_PID}" 2>/dev/null; then
    kill -INT "${LIDAR_THROTTLE_PID}" >/dev/null 2>&1 || true
    wait "${LIDAR_THROTTLE_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${RVIZ_PID}" ]] && kill -0 "${RVIZ_PID}" 2>/dev/null; then
    kill -INT "${RVIZ_PID}" >/dev/null 2>&1 || true
    wait "${RVIZ_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${LAUNCH_PID}" ]] && kill -0 "${LAUNCH_PID}" 2>/dev/null; then
    kill -INT "${LAUNCH_PID}" >/dev/null 2>&1 || true
    wait "${LAUNCH_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

mkdir -p "${RUN_DIR}"
source_env

step_log "Ensuring go2_tf_tools and go2_description are up to date for manual calibration."
colcon build --build-base build_container --install-base install_container --packages-select go2_tf_tools go2_description \
  >"${RUN_DIR}/00_colcon_build.out.log" 2>"${RUN_DIR}/00_colcon_build.err.log"
source_env

if [[ ! -f "${ROOT_DIR}/install_container/go2_description/share/go2_description/dae/base.dae" ]]; then
  step_log "FAIL go2_description mesh assets missing after build: ${ROOT_DIR}/install_container/go2_description/share/go2_description/dae/base.dae"
  exit 1
fi

detect_camera_topics() {
  local deadline topic_list aligned_depth_topic rect_depth_topic pointcloud_candidates
  deadline=$((SECONDS + 45))
  while ((SECONDS < deadline)); do
    topic_list="$(ros2 topic list 2>/dev/null || true)"
    if [[ -n "${topic_list}" ]]; then
      CAMERA_RGB_TOPIC="$(grep -E '^/camera/.*/color/image_raw$' <<<"${topic_list}" | head -n 1 || true)"
      aligned_depth_topic="$(grep -E '^/camera/.*/aligned_depth_to_color/image_raw$' <<<"${topic_list}" | head -n 1 || true)"
      rect_depth_topic="$(grep -E '^/camera/.*/depth/image_rect_raw$' <<<"${topic_list}" | head -n 1 || true)"
      CAMERA_INFO_TOPIC="$(grep -E '^/camera/.*/color/camera_info$' <<<"${topic_list}" | head -n 1 || true)"
      pointcloud_candidates="$(grep -E '^/camera/.*/depth/color/points$' <<<"${topic_list}" || true)"
      CAMERA_POINTCLOUD_TOPIC="$(head -n 1 <<<"${pointcloud_candidates}" || true)"

      CAMERA_DEPTH_TOPIC=""
      CAMERA_DEPTH_TOPIC_MODE=""
      if [[ -n "${aligned_depth_topic}" ]]; then
        CAMERA_DEPTH_TOPIC="${aligned_depth_topic}"
        CAMERA_DEPTH_TOPIC_MODE="aligned_depth_to_color"
      elif [[ -n "${rect_depth_topic}" ]]; then
        CAMERA_DEPTH_TOPIC="${rect_depth_topic}"
        CAMERA_DEPTH_TOPIC_MODE="depth_image_rect_raw"
      fi

      if [[ -n "${CAMERA_RGB_TOPIC}" && -n "${CAMERA_DEPTH_TOPIC}" && -n "${CAMERA_INFO_TOPIC}" ]]; then
        return 0
      fi
    fi
    sleep 1
  done
  return 1
}

detect_lidar_topic() {
  local topic_list
  topic_list="$(ros2 topic list 2>/dev/null || true)"
  if grep -Fxq "/utlidar/cloud" <<<"${topic_list}"; then
    LIDAR_CLOUD_TOPIC="/utlidar/cloud"
    return 0
  fi
  if grep -Fxq "/utlidar/cloud_base" <<<"${topic_list}"; then
    LIDAR_CLOUD_TOPIC="/utlidar/cloud_base"
    return 0
  fi
  return 1
}

render_rviz_config() {
  local template_path="${ROOT_DIR}/config/manual_sensor_calibration.rviz"
  local rendered_path="${RUN_DIR}/manual_sensor_calibration.runtime.rviz"
  python3 - "${template_path}" "${rendered_path}" "${RVIZ_LIDAR_TOPIC}" "${RVIZ_CAMERA_TOPIC}" <<'PY'
from pathlib import Path
import sys

template = Path(sys.argv[1]).read_text(encoding="utf-8")
template = template.replace("__LIDAR_CLOUD_TOPIC__", sys.argv[3])
template = template.replace("__CAMERA_POINTCLOUD_TOPIC__", sys.argv[4])
Path(sys.argv[2]).write_text(template, encoding="utf-8")
PY
  printf '%s\n' "${rendered_path}"
}

start_cloud_throttles() {
  step_log "Starting manual RViz cloud throttles with stamp_mode=now for base_link-fixed visualization."
  python3 "${ROOT_DIR}/scripts/rtabmap/manual_pointcloud_throttle.py" \
    --input-topic "${LIDAR_CLOUD_TOPIC}" \
    --output-topic "${RVIZ_LIDAR_TOPIC}" \
    --every-n 2 \
    --stamp-mode now \
    --label lidar \
    >"${RUN_DIR}/02_lidar_throttle.out.log" 2>"${RUN_DIR}/02_lidar_throttle.err.log" &
  LIDAR_THROTTLE_PID=$!

  python3 "${ROOT_DIR}/scripts/rtabmap/manual_pointcloud_throttle.py" \
    --input-topic "${CAMERA_POINTCLOUD_TOPIC}" \
    --output-topic "${RVIZ_CAMERA_TOPIC}" \
    --every-n 3 \
    --stamp-mode now \
    --label camera \
    >"${RUN_DIR}/02_camera_throttle.out.log" 2>"${RUN_DIR}/02_camera_throttle.err.log" &
  CAMERA_THROTTLE_PID=$!
}

step_log "Starting manual sensor calibration launch on the board/container (rviz=false; Ubuntu laptop RViz is the productive default)."
ros2 launch launch/manual_sensor_calibration.launch.py rviz:=false \
  >"${RUN_DIR}/01_launch.out.log" 2>"${RUN_DIR}/01_launch.err.log" &
LAUNCH_PID=$!

sleep 3
ros2 topic list >"${RUN_DIR}/02_topic_list_initial.log" 2>"${RUN_DIR}/02_topic_list_initial.err.log" || true

if detect_camera_topics; then
  step_log "PASS camera RGB topic detected: ${CAMERA_RGB_TOPIC}"
  step_log "PASS camera depth topic detected: ${CAMERA_DEPTH_TOPIC} (mode=${CAMERA_DEPTH_TOPIC_MODE})"
  step_log "PASS camera info topic detected: ${CAMERA_INFO_TOPIC}"
  if [[ -n "${CAMERA_POINTCLOUD_TOPIC}" ]]; then
    step_log "PASS camera pointcloud topic detected pre-RViz: ${CAMERA_POINTCLOUD_TOPIC}"
  else
    CAMERA_POINTCLOUD_TOPIC="/camera/camera/depth/color/points"
    step_log "WARN camera pointcloud topic not visible during preflight; using RViz default candidate ${CAMERA_POINTCLOUD_TOPIC} and relying on the live RealSense pointcloud path."
  fi
else
  step_log "FAIL camera topics not fully detected within timeout."
  step_log "Seen camera topics during probe:"
  grep '^/camera/' "${RUN_DIR}/02_topic_list_initial.log" | tee -a "${RUN_DIR}/summary.log" >/dev/null || true
  exit 1
fi

if detect_lidar_topic; then
  step_log "PASS lidar cloud topic detected: ${LIDAR_CLOUD_TOPIC}"
else
  step_log "FAIL lidar cloud topic not detected within timeout (/utlidar/cloud or /utlidar/cloud_base)."
  exit 1
fi

if [[ "${WITH_RVIZ}" == "1" ]]; then
  if ! ros2 pkg executables rviz2 2>/dev/null | grep -Fq "rviz2"; then
    step_log "FAIL rviz2 package/executable not available in current runtime container."
    step_log "Action: rebuild go2_board_runtime:humble via ./scripts/docker/build_board_runtime_image.sh and then rerun ./scripts/rtabmap/run_manual_sensor_calibration.sh"
    exit 1
  fi
fi

start_cloud_throttles

if [[ "${WITH_RVIZ}" == "1" ]]; then
  RVIZ_CONFIG_RENDERED="$(render_rviz_config)"
  step_log "Starting RViz with rendered config ${RVIZ_CONFIG_RENDERED}"
  ros2 run rviz2 rviz2 -d "${RVIZ_CONFIG_RENDERED}" >"${RUN_DIR}/03_rviz.out.log" 2>"${RUN_DIR}/03_rviz.err.log" &
  RVIZ_PID=$!
  sleep 5
  ros2 topic list >"${RUN_DIR}/03_topic_list_after_rviz.log" 2>"${RUN_DIR}/03_topic_list_after_rviz.err.log" || true
fi

step_log "Interactive helper starts now. Productive RViz target is the Ubuntu laptop, not the runtime container."
step_log "Default Robot Model source: repo go2_description/urdf/go2.urdf via XML-filtered sensor links + zero joint-state publisher + base_link->base bridge."
step_log "Manual calibration runs in a base_link-local visualization mode; no live odom->base_link TF is started."
step_log "LiDAR cloud topic for RViz input: ${LIDAR_CLOUD_TOPIC}"
step_log "LiDAR cloud topic rendered into RViz: ${RVIZ_LIDAR_TOPIC}"
step_log "Camera pointcloud topic for RViz input: ${CAMERA_POINTCLOUD_TOPIC}"
step_log "Camera pointcloud topic rendered into RViz: ${RVIZ_CAMERA_TOPIC}"
step_log "Manual RViz cloud policy: keep original sensor frame_id, restamp PointCloud2 header to now, Fixed Frame stays base_link."
step_log "Camera RGB topic: ${CAMERA_RGB_TOPIC}"
step_log "Camera depth topic: ${CAMERA_DEPTH_TOPIC} (mode=${CAMERA_DEPTH_TOPIC_MODE})"
step_log "Camera info topic: ${CAMERA_INFO_TOPIC}"
step_log "Manual TF overrides active: base_link->camera_link and base_link->utlidar_lidar (or configured lidar frame from helper init)."
step_log "Ubuntu laptop RViz command: ./scripts/rtabmap/run_manual_sensor_calibration_rviz.sh"
step_log "Ubuntu laptop requirement: same ROS_DOMAIN_ID and local workspace with go2_description + rviz2 sourced."

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
log_file "Robot Model default: repo go2_description/urdf/go2.urdf with XML-filtered camera_link/lidar_frame for manual TF override."
log_file "Optional non-default source found: community go2_robot_sdk/urdf/go2.urdf"
log_file "Reason for default change: community model resolved in launch, but meshes failed in RViz at runtime in this repo/container setup; the repo model keeps working mesh paths."

docker exec "${docker_exec_args[@]}" "${CONTAINER_NAME}" bash -lc \
  "cd /workspace/repo && bash ${container_run_dir}/manual_sensor_calibration_inner.sh ${container_run_dir} ${WITH_RVIZ}"
