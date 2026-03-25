#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTAINER_NAME="${CONTAINER_NAME:-go2_board_runtime}"
DB_PATH=""
MAP_YAML=""
RESTART_CONTAINER=0
PRIVILEGED=0
ALLOW_UNCALIBRATED_LIDAR=0
PC_TOPIC=""
SCAN_TOPIC="/scan"

LIDAR_FRAME="utlidar_lidar"
LIDAR_XYZ="0 0 0"
LIDAR_RPY="0 0 0"
CAMERA_FRAME="camera_link"
CAMERA_XYZ="0 0 0"
CAMERA_RPY="0 0 0"

RS_RGB_TOPIC="/camera/realsense2_camera/color/image_raw"
RS_DEPTH_TOPIC="/camera/realsense2_camera/aligned_depth_to_color/image_raw"
RS_CAMERA_INFO_TOPIC="/camera/realsense2_camera/color/camera_info"

usage() {
  cat <<'USAGE'
Usage:
  scripts/rtabmap/run_nav2_bridge_with_rtabmap_localization.sh [options]

Options:
  --db <path>                    RTAB-Map DB path (default: latest artifacts/maps/*/rtabmap.db)
  --map-yaml <path>              Static map YAML for nav2_map_server (required)
  --restart-container            Stop running container and start fresh
  --privileged                   Start/restart runtime container with ENABLE_PRIVILEGED=1
  --allow-uncalibrated-lidar     Allow lidar_xyz/lidar_rpy both "0 0 0" (debug only)
  --pc-topic <topic>             PointCloud2 input (default: prefer /utlidar/cloud then /utlidar/cloud_base)
  --scan-topic <topic>           LaserScan output topic before restamp (default: /scan)
  -h, --help                     Show this help

After the stack is up, run:
  scripts/rtabmap/smoke_test_nav2_bridge_runtime.sh
to validate bridge TF/topics/watchdog on the real productive path.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --db)
      [[ $# -lt 2 ]] && { echo "ERROR: --db requires value" >&2; exit 2; }
      DB_PATH="$2"
      shift 2
      ;;
    --map-yaml)
      [[ $# -lt 2 ]] && { echo "ERROR: --map-yaml requires value" >&2; exit 2; }
      MAP_YAML="$2"
      shift 2
      ;;
    --restart-container)
      RESTART_CONTAINER=1
      shift
      ;;
    --privileged)
      PRIVILEGED=1
      shift
      ;;
    --allow-uncalibrated-lidar)
      ALLOW_UNCALIBRATED_LIDAR=1
      shift
      ;;
    --pc-topic)
      [[ $# -lt 2 ]] && { echo "ERROR: --pc-topic requires value" >&2; exit 2; }
      PC_TOPIC="$2"
      shift 2
      ;;
    --scan-topic)
      [[ $# -lt 2 ]] && { echo "ERROR: --scan-topic requires value" >&2; exit 2; }
      SCAN_TOPIC="$2"
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

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker CLI not found" >&2
  exit 1
fi

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${ROOT_DIR}/artifacts/nav2_bridge/${TIMESTAMP}"
mkdir -p "${RUN_DIR}"
SUMMARY_LOG="${RUN_DIR}/summary.log"
INNER_SCRIPT_HOST="${RUN_DIR}/nav2_bridge_inner.sh"

log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "${SUMMARY_LOG}"
}

container_running() {
  docker ps --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"
}

latest_db() {
  local latest_dir
  latest_dir="$(ls -1d "${ROOT_DIR}/artifacts/maps"/* 2>/dev/null | sort | tail -n 1 || true)"
  [[ -n "${latest_dir}" && -f "${latest_dir}/rtabmap.db" ]] && echo "${latest_dir}/rtabmap.db"
}

host_db_path=""
if [[ -n "${DB_PATH}" ]]; then
  if [[ "${DB_PATH}" = /* ]]; then
    host_db_path="${DB_PATH}"
  else
    host_db_path="${ROOT_DIR}/${DB_PATH}"
  fi
else
  host_db_path="$(latest_db || true)"
fi

if [[ -z "${host_db_path}" || ! -f "${host_db_path}" ]]; then
  log "FAIL: rtabmap DB not found. Provide --db or ensure artifacts/maps/*/rtabmap.db exists."
  exit 1
fi

if [[ -z "${MAP_YAML}" ]]; then
  log "FAIL: --map-yaml is required (static map for nav2_map_server)."
  exit 1
fi

container_db_path="${host_db_path}"
if [[ "${host_db_path}" == "${ROOT_DIR}"/* ]]; then
  container_db_path="/workspace/repo/${host_db_path#${ROOT_DIR}/}"
fi

host_map_yaml_path=""
if [[ "${MAP_YAML}" = /* ]]; then
  host_map_yaml_path="${MAP_YAML}"
else
  host_map_yaml_path="${ROOT_DIR}/${MAP_YAML}"
fi
if [[ ! -f "${host_map_yaml_path}" ]]; then
  log "FAIL: map yaml not found: ${host_map_yaml_path}"
  exit 1
fi

container_map_yaml_path="${host_map_yaml_path}"
if [[ "${host_map_yaml_path}" == "${ROOT_DIR}"/* ]]; then
  container_map_yaml_path="/workspace/repo/${host_map_yaml_path#${ROOT_DIR}/}"
fi

if container_running && [[ "${RESTART_CONTAINER}" -eq 1 ]]; then
  log "Stopping running container '${CONTAINER_NAME}' (--restart-container)."
  docker stop "${CONTAINER_NAME}" >>"${RUN_DIR}/00_container_manage.out.log" 2>>"${RUN_DIR}/00_container_manage.err.log"
fi

if ! container_running; then
  log "Starting runtime container '${CONTAINER_NAME}' via run_board_runtime.sh --run 'sleep infinity' (privileged=${PRIVILEGED})."
  if [[ "${PRIVILEGED}" -eq 1 ]]; then
    ENABLE_PRIVILEGED=1 CONTAINER_NAME="${CONTAINER_NAME}" \
      "${ROOT_DIR}/scripts/bringup/run_board_runtime.sh" --run "sleep infinity" \
      >"${RUN_DIR}/00_runtime_start.out.log" 2>"${RUN_DIR}/00_runtime_start.err.log" &
  else
    CONTAINER_NAME="${CONTAINER_NAME}" \
      "${ROOT_DIR}/scripts/bringup/run_board_runtime.sh" --run "sleep infinity" \
      >"${RUN_DIR}/00_runtime_start.out.log" 2>"${RUN_DIR}/00_runtime_start.err.log" &
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
    log "FAIL: runtime container did not become ready."
    exit 1
  fi
fi

cat >"${INNER_SCRIPT_HOST}" <<'INNER_EOF'
#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_DIR="$1"
DB_PATH="$2"
PC_TOPIC_REQUESTED="$3"
SCAN_TOPIC="$4"
ALLOW_UNCALIBRATED_LIDAR="$5"
LIDAR_FRAME="$6"
LIDAR_XYZ="$7"
LIDAR_RPY="$8"
CAMERA_FRAME="$9"
CAMERA_XYZ="${10}"
CAMERA_RPY="${11}"
RS_RGB_TOPIC="${12}"
RS_DEPTH_TOPIC="${13}"
RS_CAMERA_INFO_TOPIC="${14}"
MAP_YAML_PATH="${15}"
ROOT_DIR="/workspace/repo"

SCAN_FRESH_TOPIC="${SCAN_TOPIC%/}_fresh"
SCAN_RESTAMP_HELPER="${ROOT_DIR}/scripts/slam_toolbox/scan_restamp.py"
NAV2_PARAMS_FILE="${ROOT_DIR}/config/nav2_rtabmap_lidar_params.yaml"
NAV2_LAUNCH_FILE="${ROOT_DIR}/launch/nav2_rtabmap.launch.py"
BRIDGE_CONFIG_FILE="${ROOT_DIR}/src/go2_nav2_bridge/config/bridge.yaml"

BOARD_PID=""
REALSENSE_PID=""
PC2LS_PID=""
SCAN_RESTAMP_PID=""
LOCALIZATION_PID=""
NAV2_PID=""

mkdir -p "${ARTIFACT_DIR}"

step_log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "${ARTIFACT_DIR}/summary.log"
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

start_bg() {
  local cmd="$1"
  local out_log="$2"
  local err_log="$3"
  set +e
  eval "${cmd}" >"${out_log}" 2>"${err_log}" &
  local pid=$!
  set -e
  echo "${pid}"
}

stop_pid() {
  local pid="$1"
  local name="$2"
  [[ -z "${pid}" ]] && return
  if kill -0 "${pid}" 2>/dev/null; then
    kill -INT "${pid}" >/dev/null 2>&1 || true
    for _ in $(seq 1 8); do
      if ! kill -0 "${pid}" 2>/dev/null; then
        step_log "Stopped ${name} (pid=${pid})."
        return
      fi
      sleep 1
    done
    kill -TERM "${pid}" >/dev/null 2>&1 || true
    wait "${pid}" >/dev/null 2>&1 || true
    step_log "Stopped ${name} (pid=${pid})."
  fi
}

cleanup() {
  set +e
  stop_pid "${NAV2_PID}" "nav2_plus_bridge"
  stop_pid "${LOCALIZATION_PID}" "rtabmap_localization"
  stop_pid "${SCAN_RESTAMP_PID}" "scan_restamp"
  stop_pid "${PC2LS_PID}" "pointcloud_to_laserscan"
  stop_pid "${REALSENSE_PID}" "realsense"
  stop_pid "${BOARD_PID}" "board_description"
}
trap cleanup EXIT INT TERM

normalize_triplet() {
  echo "$1" | awk '{$1=$1; print}'
}

is_zero_triplet() {
  [[ "$(normalize_triplet "$1")" == "0 0 0" ]]
}

wait_tf_resolved() {
  local parent="$1"
  local child="$2"
  local timeout_sec="$3"
  local start_ts="$(date +%s)"

  while true; do
    local elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi
    set +e
    timeout 3s ros2 run tf2_ros tf2_echo "${parent}" "${child}" >"${ARTIFACT_DIR}/tf_${parent}_to_${child}.out.log" 2>"${ARTIFACT_DIR}/tf_${parent}_to_${child}.err.log"
    local rc=$?
    set -e
    if [[ "${rc}" -eq 0 ]] || grep -Eq "At time|Translation:|Rotation:" "${ARTIFACT_DIR}/tf_${parent}_to_${child}.out.log"; then
      return 0
    fi
    sleep 1
  done
}

wait_once_topic() {
  local topic="$1"
  local timeout_sec="$2"
  local out_file="$3"
  local err_file="$4"

  set +e
  timeout "${timeout_sec}" ros2 topic echo --once "${topic}" --qos-reliability best_effort >"${out_file}" 2>"${err_file}"
  local rc=$?
  set -e
  if [[ "${rc}" -eq 0 ]]; then
    return 0
  fi

  set +e
  timeout "${timeout_sec}" ros2 topic echo --once "${topic}" >"${out_file}" 2>"${err_file}"
  rc=$?
  set -e
  return "${rc}"
}

wait_realsense_ready() {
  local timeout_sec="$1"
  local start_ts="$(date +%s)"

  while true; do
    local elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi

    ros2 topic list >"${ARTIFACT_DIR}/realsense_topics_all.log" 2>/dev/null || true
    if grep -Fxq "${RS_RGB_TOPIC}" "${ARTIFACT_DIR}/realsense_topics_all.log" \
      && grep -Fxq "${RS_DEPTH_TOPIC}" "${ARTIFACT_DIR}/realsense_topics_all.log" \
      && grep -Fxq "${RS_CAMERA_INFO_TOPIC}" "${ARTIFACT_DIR}/realsense_topics_all.log"; then
      set +e
      timeout 6s ros2 topic echo --once "${RS_CAMERA_INFO_TOPIC}" >"${ARTIFACT_DIR}/realsense_camera_info_probe.out.log" 2>"${ARTIFACT_DIR}/realsense_camera_info_probe.err.log"
      local rc=$?
      set -e
      [[ "${rc}" -eq 0 ]] && return 0
    fi

    sleep 1
  done
}

pick_lidar_topic() {
  local candidates=()
  if [[ -n "${PC_TOPIC_REQUESTED}" ]]; then
    candidates=("${PC_TOPIC_REQUESTED}")
  else
    candidates=("/utlidar/cloud" "/utlidar/cloud_base")
  fi

  ros2 topic list >"${ARTIFACT_DIR}/topics_all.log" 2>/dev/null || true
  for c in "${candidates[@]}"; do
    if grep -Fxq "${c}" "${ARTIFACT_DIR}/topics_all.log"; then
      for qos in reliable best_effort ""; do
        set +e
        if [[ -n "${qos}" ]]; then
          timeout 8s ros2 topic echo --once "${c}" --qos-reliability "${qos}" >"${ARTIFACT_DIR}/lidar_probe.out.log" 2>"${ARTIFACT_DIR}/lidar_probe.err.log"
        else
          timeout 8s ros2 topic echo --once "${c}" >"${ARTIFACT_DIR}/lidar_probe.out.log" 2>"${ARTIFACT_DIR}/lidar_probe.err.log"
        fi
        local rc=$?
        set -e
        if [[ "${rc}" -eq 0 ]]; then
          LIDAR_PC_TOPIC_USED="${c}"
          return 0
        fi
      done
    fi
  done
  return 1
}

wait_topic_type() {
  local topic="$1"
  local timeout_sec="$2"
  local start_ts="$(date +%s)"

  while true; do
    local elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi
    set +e
    ros2 topic type "${topic}" >"${ARTIFACT_DIR}/topic_type_$(basename "${topic}").out.log" 2>"${ARTIFACT_DIR}/topic_type_$(basename "${topic}").err.log"
    local rc=$?
    set -e
    if [[ "${rc}" -eq 0 ]]; then
      return 0
    fi
    sleep 1
  done
}

wait_node_visible() {
  local node_name="$1"
  local timeout_sec="$2"
  local start_ts="$(date +%s)"

  while true; do
    local elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi
    ros2 node list >"${ARTIFACT_DIR}/nodes_all.log" 2>/dev/null || true
    if grep -Fxq "${node_name}" "${ARTIFACT_DIR}/nodes_all.log"; then
      return 0
    fi
    sleep 1
  done
}

wait_nav2_lifecycle_active() {
  local timeout_sec="$1"
  local start_ts="$(date +%s)"
  local nodes=(/map_server /controller_server /planner_server /behavior_server /bt_navigator /waypoint_follower)

  while true; do
    local elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi
    local all_active=1
    for n in "${nodes[@]}"; do
      local state_log="${ARTIFACT_DIR}/lifecycle_${n#/}.out.log"
      set +e
      ros2 lifecycle get "${n}" >"${state_log}" 2>&1
      local rc=$?
      set -e
      if [[ "${rc}" -ne 0 ]] || ! grep -qi "active" "${state_log}"; then
        all_active=0
      fi
    done
    if [[ "${all_active}" -eq 1 ]]; then
      return 0
    fi
    sleep 1
  done
}

wait_map_ready() {
  local timeout_sec="$1"
  local start_ts="$(date +%s)"

  while true; do
    local elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi
    if wait_topic_type "/map" 1; then
      set +e
      timeout 10s ros2 topic echo --once /map >"${ARTIFACT_DIR}/map_probe.out.log" 2>"${ARTIFACT_DIR}/map_probe.err.log"
      local rc=$?
      set -e
      [[ "${rc}" -eq 0 ]] && return 0
    fi
    sleep 1
  done
}

check_map_owner() {
  ros2 topic info /map -v >"${ARTIFACT_DIR}/map_topic_info.out.log" 2>"${ARTIFACT_DIR}/map_topic_info.err.log" || true
  grep -Eq "Node name:[[:space:]]*/map_server|Node name:[[:space:]]*map_server" "${ARTIFACT_DIR}/map_topic_info.out.log"
}

source_env

ensure_bridge_package() {
  if ros2 pkg prefix go2_nav2_bridge >"${ARTIFACT_DIR}/bridge_pkg_prefix.out.log" 2>"${ARTIFACT_DIR}/bridge_pkg_prefix.err.log"; then
    step_log "PASS go2_nav2_bridge package is already available in the sourced overlay."
    return 0
  fi

  step_log "INFO: go2_nav2_bridge not yet available in overlay; attempting focused build."
  if ! command -v colcon >/dev/null 2>&1; then
    step_log "FAIL: colcon not found in runtime container, cannot build go2_nav2_bridge."
    return 1
  fi

  colcon build --build-base "${ROOT_DIR}/build_container" --install-base "${ROOT_DIR}/install_container" --packages-select go2_nav2_bridge \
    >"${ARTIFACT_DIR}/00_bridge_build.out.log" 2>"${ARTIFACT_DIR}/00_bridge_build.err.log" || return 1

  source "${ROOT_DIR}/install_container/setup.bash"
  ros2 pkg prefix go2_nav2_bridge >"${ARTIFACT_DIR}/bridge_pkg_prefix.out.log" 2>"${ARTIFACT_DIR}/bridge_pkg_prefix.err.log"
}

if [[ ! -f "${DB_PATH}" ]]; then
  step_log "FAIL: DB path not found inside container: ${DB_PATH}"
  exit 1
fi
if [[ ! -f "${SCAN_RESTAMP_HELPER}" ]]; then
  step_log "FAIL: scan_restamp helper not found: ${SCAN_RESTAMP_HELPER}"
  exit 1
fi
if [[ ! -f "${NAV2_PARAMS_FILE}" ]]; then
  step_log "FAIL: nav2 params file missing: ${NAV2_PARAMS_FILE}"
  exit 1
fi
if [[ ! -f "${NAV2_LAUNCH_FILE}" ]]; then
  step_log "FAIL: nav2 launch missing: ${NAV2_LAUNCH_FILE}"
  exit 1
fi
if [[ ! -f "${BRIDGE_CONFIG_FILE}" ]]; then
  step_log "FAIL: bridge config missing: ${BRIDGE_CONFIG_FILE}"
  exit 1
fi
if [[ ! -f "${MAP_YAML_PATH}" ]]; then
  step_log "FAIL: map yaml missing inside container: ${MAP_YAML_PATH}"
  exit 1
fi
if ! ensure_bridge_package; then
  step_log "FAIL: ros2 cannot resolve package go2_nav2_bridge after focused build attempt."
  exit 1
fi

if is_zero_triplet "${LIDAR_XYZ}" && is_zero_triplet "${LIDAR_RPY}" && [[ "${ALLOW_UNCALIBRATED_LIDAR}" -ne 1 ]]; then
  step_log "FAIL: lidar_xyz and lidar_rpy are both zero. Use calibrated values or --allow-uncalibrated-lidar."
  exit 1
fi

step_log "Starting board_description launch."
BOARD_PID="$(start_bg \
  "ros2 launch launch/board_description.launch.py lidar_tf_required:=true lidar_frame:=${LIDAR_FRAME} lidar_xyz:='${LIDAR_XYZ}' lidar_rpy:='${LIDAR_RPY}' camera_tf_required:=true camera_frame:=${CAMERA_FRAME} camera_xyz:='${CAMERA_XYZ}' camera_rpy:='${CAMERA_RPY}'" \
  "${ARTIFACT_DIR}/01_board_description.out.log" \
  "${ARTIFACT_DIR}/01_board_description.err.log")"

wait_tf_resolved "base_link" "${LIDAR_FRAME}" 25 || { step_log "FAIL: TF not resolvable base_link->${LIDAR_FRAME}"; exit 1; }
wait_tf_resolved "base_link" "${CAMERA_FRAME}" 25 || { step_log "FAIL: TF not resolvable base_link->${CAMERA_FRAME}"; exit 1; }
wait_tf_resolved "odom" "base_link" 25 || { step_log "FAIL: TF not resolvable odom->base_link"; exit 1; }
step_log "PASS board_description TF preflight."

step_log "Starting realsense launch."
REALSENSE_PID="$(start_bg \
  "ros2 launch launch/realsense_board.launch.py" \
  "${ARTIFACT_DIR}/02_realsense.out.log" \
  "${ARTIFACT_DIR}/02_realsense.err.log")"
wait_realsense_ready 60 || { step_log "FAIL: RealSense preflight failed."; exit 1; }
step_log "PASS RealSense preflight."

pick_lidar_topic || { step_log "FAIL: LiDAR mandatory but no readable pointcloud topic found."; exit 1; }
step_log "PASS LiDAR sample read: topic=${LIDAR_PC_TOPIC_USED}"

step_log "Starting pointcloud_to_laserscan (${LIDAR_PC_TOPIC_USED} -> ${SCAN_TOPIC})."
PC2LS_PID="$(start_bg \
  "ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node --ros-args -p target_frame:=base_link -p min_height:=-0.30 -p max_height:=0.50 -p range_min:=0.10 -p range_max:=30.0 -r cloud_in:=${LIDAR_PC_TOPIC_USED} -r scan:=${SCAN_TOPIC}" \
  "${ARTIFACT_DIR}/03_pc2ls.out.log" \
  "${ARTIFACT_DIR}/03_pc2ls.err.log")"
wait_once_topic "${SCAN_TOPIC}" 12s "${ARTIFACT_DIR}/03_scan_probe.out.log" "${ARTIFACT_DIR}/03_scan_probe.err.log" || { step_log "FAIL: ${SCAN_TOPIC} not publishing."; exit 1; }
step_log "PASS ${SCAN_TOPIC} publishing."

step_log "Starting scan_restamp (${SCAN_TOPIC} -> ${SCAN_FRESH_TOPIC})."
SCAN_RESTAMP_PID="$(start_bg \
  "python3 ${SCAN_RESTAMP_HELPER} ${SCAN_TOPIC} ${SCAN_FRESH_TOPIC}" \
  "${ARTIFACT_DIR}/04_scan_restamp.out.log" \
  "${ARTIFACT_DIR}/04_scan_restamp.err.log")"
wait_once_topic "${SCAN_FRESH_TOPIC}" 12s "${ARTIFACT_DIR}/04_scan_fresh_probe.out.log" "${ARTIFACT_DIR}/04_scan_fresh_probe.err.log" || { step_log "FAIL: ${SCAN_FRESH_TOPIC} not publishing."; exit 1; }
step_log "PASS ${SCAN_FRESH_TOPIC} publishing."

step_log "Starting RTAB-Map localization."
LOCALIZATION_PID="$(start_bg \
  "ros2 launch launch/rtabmap_localization.launch.py database_path:='${DB_PATH}' rgb_topic:=${RS_RGB_TOPIC} depth_topic:=${RS_DEPTH_TOPIC} camera_info_topic:=${RS_CAMERA_INFO_TOPIC} scan_topic:=${SCAN_FRESH_TOPIC} base_frame:=base_link odom_frame:=odom map_frame:=map map_topic:=/rtabmap/map" \
  "${ARTIFACT_DIR}/05_localization.out.log" \
  "${ARTIFACT_DIR}/05_localization.err.log")"

sleep 3
kill -0 "${LOCALIZATION_PID}" 2>/dev/null || { step_log "FAIL: RTAB-Map localization exited early."; exit 1; }
wait_tf_resolved "map" "odom" 25 || { step_log "FAIL: Localization TF not resolvable (map->odom)."; exit 1; }
wait_once_topic "/rgbd_image" 12s "${ARTIFACT_DIR}/05_rgbd_image_probe.out.log" "${ARTIFACT_DIR}/05_rgbd_image_probe.err.log" || { step_log "FAIL: Localization input /rgbd_image not readable."; exit 1; }
wait_once_topic "${SCAN_FRESH_TOPIC}" 8s "${ARTIFACT_DIR}/05_scan_fresh_input_probe.out.log" "${ARTIFACT_DIR}/05_scan_fresh_input_probe.err.log" || { step_log "FAIL: Localization input ${SCAN_FRESH_TOPIC} not readable."; exit 1; }
step_log "PASS localization up."

step_log "Starting Nav2 + bridge bringup."
NAV2_PID="$(start_bg \
  "ros2 launch launch/nav2_rtabmap.launch.py params_file:=${NAV2_PARAMS_FILE} bridge_params_file:=${BRIDGE_CONFIG_FILE} scan_topic:=${SCAN_FRESH_TOPIC} map_yaml:=${MAP_YAML_PATH}" \
  "${ARTIFACT_DIR}/06_nav2_bridge.out.log" \
  "${ARTIFACT_DIR}/06_nav2_bridge.err.log")"

sleep 8
wait_map_ready 30 || { step_log "FAIL: /map not received from nav2_map_server."; exit 1; }
check_map_owner || { step_log "FAIL: /map ownership check failed."; exit 1; }
wait_nav2_lifecycle_active 25 || { step_log "FAIL: Nav2 lifecycle nodes did not reach active state."; exit 1; }
wait_node_visible "/go2_nav2_bridge" 15 || { step_log "FAIL: /go2_nav2_bridge node not visible."; exit 1; }
wait_tf_resolved "base_link" "base_link_nav2" 20 || { step_log "FAIL: TF not resolvable base_link->base_link_nav2."; exit 1; }
wait_topic_type "/cmd_vel_nav2" 15 || { step_log "FAIL: /cmd_vel_nav2 type not resolvable."; exit 1; }

ros2 action list >"${ARTIFACT_DIR}/07_actions_all.log" 2>/dev/null || true
grep -Fxq "/compute_path_to_pose" "${ARTIFACT_DIR}/07_actions_all.log" || { step_log "FAIL: Planner interface /compute_path_to_pose not visible."; exit 1; }
grep -Fxq "/follow_path" "${ARTIFACT_DIR}/07_actions_all.log" || { step_log "FAIL: Controller interface /follow_path not visible."; exit 1; }

step_log "PASS Nav2 + bridge bringup checks complete. Stack is running. Press Ctrl+C to stop."
step_log "Next smoke step on the host: ./scripts/rtabmap/smoke_test_nav2_bridge_runtime.sh"
while true; do
  sleep 1
done
INNER_EOF

chmod +x "${INNER_SCRIPT_HOST}"

log "Run dir: ${RUN_DIR}"
log "DB: ${host_db_path}"
log "Map YAML: ${host_map_yaml_path}"

set +e
docker exec "${CONTAINER_NAME}" bash -lc \
  "/workspace/repo/artifacts/nav2_bridge/${TIMESTAMP}/nav2_bridge_inner.sh /workspace/repo/artifacts/nav2_bridge/${TIMESTAMP} '${container_db_path}' '${PC_TOPIC}' '${SCAN_TOPIC}' '${ALLOW_UNCALIBRATED_LIDAR}' '${LIDAR_FRAME}' '${LIDAR_XYZ}' '${LIDAR_RPY}' '${CAMERA_FRAME}' '${CAMERA_XYZ}' '${CAMERA_RPY}' '${RS_RGB_TOPIC}' '${RS_DEPTH_TOPIC}' '${RS_CAMERA_INFO_TOPIC}' '${container_map_yaml_path}'" \
  > >(tee "${RUN_DIR}/99_inner_wrapper.out.log") \
  2> >(tee "${RUN_DIR}/99_inner_wrapper.err.log" >&2)
RC=$?
set -e

if [[ ${RC} -ne 0 ]]; then
  log "FAIL: Nav2+bridge bringup with RTAB-Map localization failed (rc=${RC})."
  log "Inspect ${RUN_DIR}/summary.log and component logs under ${RUN_DIR}."
  exit "${RC}"
fi

log "Stopped nav2+bridge bringup stack."
