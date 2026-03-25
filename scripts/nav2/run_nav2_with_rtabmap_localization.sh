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
  scripts/nav2/run_nav2_with_rtabmap_localization.sh [options]

Options:
  --db <path>                    RTAB-Map DB path (default: latest artifacts/maps/*/rtabmap.db)
  --map-yaml <path>              Static map YAML for nav2_map_server (required)
  --restart-container            Stop running container and start fresh
  --privileged                   Start/restart runtime container with ENABLE_PRIVILEGED=1
  --allow-uncalibrated-lidar     Allow lidar_xyz/lidar_rpy both "0 0 0" (debug only)
  --pc-topic <topic>             PointCloud2 input (default: prefer /utlidar/cloud then /utlidar/cloud_base)
  --scan-topic <topic>           LaserScan output topic before restamp (default: /scan)
  -h, --help                     Show this help
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

require_nonempty() {
  local name="$1"
  local value="$2"
  if [[ -z "${value}" ]]; then
    echo "ERROR: required variable '${name}' is empty" >&2
    exit 1
  fi
}

require_nonempty "RS_RGB_TOPIC" "${RS_RGB_TOPIC}"
require_nonempty "RS_DEPTH_TOPIC" "${RS_DEPTH_TOPIC}"
require_nonempty "RS_CAMERA_INFO_TOPIC" "${RS_CAMERA_INFO_TOPIC}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${ROOT_DIR}/artifacts/nav2/${TIMESTAMP}"
mkdir -p "${RUN_DIR}"
SUMMARY_LOG="${RUN_DIR}/summary.log"
INNER_SCRIPT_HOST="${RUN_DIR}/nav2_inner.sh"

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
  stop_pid "${NAV2_PID}" "nav2"
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
  local attempt=0
  local parent_tag="${parent#/}"
  local child_tag="${child#/}"
  local attempts_dir="${ARTIFACT_DIR}/02_tf_resolve_${parent_tag}_to_${child_tag}"

  TF_RESOLVE_MATCH_ATTEMPT=""
  TF_RESOLVE_LAST_OUT=""
  TF_RESOLVE_LAST_ERR=""
  mkdir -p "${attempts_dir}"

  while true; do
    local elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi

    attempt=$((attempt + 1))
    local out_log="${attempts_dir}/attempt_${attempt}.out.log"
    local err_log="${attempts_dir}/attempt_${attempt}.err.log"

    set +e
    timeout 3s ros2 run tf2_ros tf2_echo "${parent}" "${child}" >"${out_log}" 2>"${err_log}"
    local rc=$?
    set -e

    TF_RESOLVE_LAST_OUT="${out_log}"
    TF_RESOLVE_LAST_ERR="${err_log}"
    if [[ "${rc}" -eq 0 ]] || grep -Eq "At time|Translation:|Rotation:" "${out_log}"; then
      TF_RESOLVE_MATCH_ATTEMPT="${attempt}"
      return 0
    fi

    sleep 1
  done
}

collect_goal_pose_diagnostics() {
  ros2 node list >"${ARTIFACT_DIR}/10_diag_nodes_all.log" 2>"${ARTIFACT_DIR}/10_diag_nodes_all.err.log" || true
  ros2 topic list >"${ARTIFACT_DIR}/10_diag_topics_all.log" 2>"${ARTIFACT_DIR}/10_diag_topics_all.err.log" || true
  grep -E '^/map$|^/rtabmap/map$|nav2|scan|rtabmap' "${ARTIFACT_DIR}/10_diag_topics_all.log" \
    >"${ARTIFACT_DIR}/10_diag_topics_filtered.log" || true

  ros2 topic info /map -v >"${ARTIFACT_DIR}/10_diag_map_topic_info.out.log" 2>"${ARTIFACT_DIR}/10_diag_map_topic_info.err.log" || true
  ros2 topic info /nav2/cmd_vel >"${ARTIFACT_DIR}/10_diag_nav2_cmd_vel_topic_info.out.log" 2>"${ARTIFACT_DIR}/10_diag_nav2_cmd_vel_topic_info.err.log" || true
  ros2 topic info /rtabmap/map -v >"${ARTIFACT_DIR}/10_diag_rtabmap_map_topic_info.out.log" 2>"${ARTIFACT_DIR}/10_diag_rtabmap_map_topic_info.err.log" || true

  ros2 lifecycle nodes >"${ARTIFACT_DIR}/10_diag_lifecycle_nodes.out.log" 2>"${ARTIFACT_DIR}/10_diag_lifecycle_nodes.err.log" || true
  : >"${ARTIFACT_DIR}/10_diag_lifecycle_states.out.log"
  for n in /map_server /controller_server /planner_server /behavior_server /bt_navigator /waypoint_follower /lifecycle_manager_navigation; do
    {
      echo ">>> ${n}"
      ros2 lifecycle get "${n}"
    } >>"${ARTIFACT_DIR}/10_diag_lifecycle_states.out.log" 2>&1 || true
  done

  step_log "Diagnostics: ros2 node list"
  cat "${ARTIFACT_DIR}/10_diag_nodes_all.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  step_log "Diagnostics: lifecycle states"
  cat "${ARTIFACT_DIR}/10_diag_lifecycle_states.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  step_log "Diagnostics: /map topic info (-v)"
  cat "${ARTIFACT_DIR}/10_diag_map_topic_info.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  step_log "Diagnostics: /nav2/cmd_vel topic info"
  cat "${ARTIFACT_DIR}/10_diag_nav2_cmd_vel_topic_info.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  step_log "Diagnostics: filtered topics (map/nav2/scan/rtabmap)"
  cat "${ARTIFACT_DIR}/10_diag_topics_filtered.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  step_log "Diagnostics: localization log tail (120)"
  tail -n 120 "${ARTIFACT_DIR}/05_localization.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  tail -n 120 "${ARTIFACT_DIR}/05_localization.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  step_log "Diagnostics: nav2 log tail (120)"
  tail -n 120 "${ARTIFACT_DIR}/06_nav2.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  tail -n 120 "${ARTIFACT_DIR}/06_nav2.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
}

fail_goal_pose_readiness() {
  local msg="$1"
  step_log "FAIL: ${msg}"
  collect_goal_pose_diagnostics
  exit 1
}

wait_realsense_ready() {
  local timeout_sec="$1"
  local start_ts="$(date +%s)"

  while true; do
    local elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi

    set +e
    ros2 topic list >"${ARTIFACT_DIR}/04_realsense_topics_all.log" 2>/dev/null
    set -e

    if grep -Fxq "/camera/realsense2_camera/color/image_raw" "${ARTIFACT_DIR}/04_realsense_topics_all.log" \
      && grep -Fxq "/camera/realsense2_camera/aligned_depth_to_color/image_raw" "${ARTIFACT_DIR}/04_realsense_topics_all.log" \
      && grep -Fxq "/camera/realsense2_camera/color/camera_info" "${ARTIFACT_DIR}/04_realsense_topics_all.log"; then
      set +e
      timeout 6s ros2 topic echo --once /camera/realsense2_camera/color/camera_info >"${ARTIFACT_DIR}/04_realsense_camera_info_probe.out.log" 2>"${ARTIFACT_DIR}/04_realsense_camera_info_probe.err.log"
      local rc=$?
      set -e
      [[ "${rc}" -eq 0 ]] && return 0
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

wait_scan_fresh_ready() {
  local timeout_sec="$1"
  local start_ts="$(date +%s)"

  while true; do
    local elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi

    set +e
    timeout 6s ros2 topic echo --once "${SCAN_FRESH_TOPIC}" --qos-reliability best_effort \
      >"${ARTIFACT_DIR}/04_scan_fresh_probe.out.log" \
      2>"${ARTIFACT_DIR}/04_scan_fresh_probe.err.log"
    local rc=$?
    set -e

    if [[ "${rc}" -eq 0 ]]; then
      return 0
    fi

    set +e
    timeout 6s ros2 topic echo --once "${SCAN_FRESH_TOPIC}" \
      >"${ARTIFACT_DIR}/04_scan_fresh_probe_plain.out.log" \
      2>"${ARTIFACT_DIR}/04_scan_fresh_probe_plain.err.log"
    rc=$?
    set -e

    if [[ "${rc}" -eq 0 ]]; then
      return 0
    fi

    sleep 1
  done
}

wait_scan_ready() {
  local topic="$1"
  local timeout_sec="$2"
  local start_ts="$(date +%s)"
  local supports_qos_flag=0

  set +e
  ros2 topic echo --help 2>&1 | grep -q -- '--qos-reliability'
  if [[ $? -eq 0 ]]; then
    supports_qos_flag=1
  fi
  set -e

  while true; do
    local elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi

    if [[ "${supports_qos_flag}" -eq 1 ]]; then
      set +e
      timeout 6s ros2 topic echo --once "${topic}" --qos-reliability best_effort \
        >"${ARTIFACT_DIR}/03_scan_probe.best_effort.out.log" \
        2>"${ARTIFACT_DIR}/03_scan_probe.best_effort.err.log"
      local rc=$?
      set -e
      if [[ "${rc}" -eq 0 ]]; then
        cp -f "${ARTIFACT_DIR}/03_scan_probe.best_effort.out.log" "${ARTIFACT_DIR}/03_scan_probe.out.log" 2>/dev/null || true
        cp -f "${ARTIFACT_DIR}/03_scan_probe.best_effort.err.log" "${ARTIFACT_DIR}/03_scan_probe.err.log" 2>/dev/null || true
        return 0
      fi
    fi

    set +e
    timeout 6s ros2 topic echo --once "${topic}" \
      >"${ARTIFACT_DIR}/03_scan_probe.plain.out.log" \
      2>"${ARTIFACT_DIR}/03_scan_probe.plain.err.log"
    local rc=$?
    set -e
    if [[ "${rc}" -eq 0 ]]; then
      cp -f "${ARTIFACT_DIR}/03_scan_probe.plain.out.log" "${ARTIFACT_DIR}/03_scan_probe.out.log" 2>/dev/null || true
      cp -f "${ARTIFACT_DIR}/03_scan_probe.plain.err.log" "${ARTIFACT_DIR}/03_scan_probe.err.log" 2>/dev/null || true
      return 0
    fi

    sleep 1
  done
}

dump_scan_diagnostics() {
  local topic="$1"
  ros2 topic info "${topic}" -v >"${ARTIFACT_DIR}/03_scan_topic_info.out.log" 2>"${ARTIFACT_DIR}/03_scan_topic_info.err.log" || true
  ros2 topic list >"${ARTIFACT_DIR}/03_scan_topics_all.out.log" 2>"${ARTIFACT_DIR}/03_scan_topics_all.err.log" || true
  grep -E '^/utlidar/cloud$|^/utlidar/cloud_base$|^/scan$|^/scan_fresh$' "${ARTIFACT_DIR}/03_scan_topics_all.out.log" \
    >"${ARTIFACT_DIR}/03_scan_topics_filtered.out.log" || true

  step_log "Scan diagnostics: ros2 topic info ${topic} -v"
  cat "${ARTIFACT_DIR}/03_scan_topic_info.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  step_log "Scan diagnostics: filtered topic list (/utlidar/cloud, /scan, /scan_fresh)"
  cat "${ARTIFACT_DIR}/03_scan_topics_filtered.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  step_log "Scan diagnostics: best_effort probe stderr (if available)"
  cat "${ARTIFACT_DIR}/03_scan_probe.best_effort.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  step_log "Scan diagnostics: plain probe stderr"
  cat "${ARTIFACT_DIR}/03_scan_probe.plain.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  step_log "Scan diagnostics: pointcloud_to_laserscan log tail (80)"
  tail -n 80 "${ARTIFACT_DIR}/03_pc2ls.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  tail -n 80 "${ARTIFACT_DIR}/03_pc2ls.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
}

wait_map_ready() {
  local timeout_sec="$1"
  local start_ts="$(date +%s)"

  while true; do
    local elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi

    set +e
    ros2 topic type /map >"${ARTIFACT_DIR}/05_map_topic_type.out.log" 2>"${ARTIFACT_DIR}/05_map_topic_type.err.log"
    local type_rc=$?
    set -e

    if [[ "${type_rc}" -eq 0 ]] && grep -q . "${ARTIFACT_DIR}/05_map_topic_type.out.log"; then
      set +e
      timeout 10s ros2 topic echo --once /map \
        >"${ARTIFACT_DIR}/05_map_probe.out.log" \
        2>"${ARTIFACT_DIR}/05_map_probe.err.log"
      local echo_rc=$?
      set -e
      if [[ "${echo_rc}" -eq 0 ]]; then
        return 0
      fi
    fi

    sleep 1
  done
}

check_map_owner() {
  ros2 topic info /map -v >"${ARTIFACT_DIR}/06_map_topic_info.out.log" 2>"${ARTIFACT_DIR}/06_map_topic_info.err.log" || true

  if ! grep -Eq "Node name:[[:space:]]*/map_server|Node name:[[:space:]]*map_server" "${ARTIFACT_DIR}/06_map_topic_info.out.log"; then
    step_log "FAIL: /map does not show map_server as publisher."
    return 1
  fi

  local publisher_count
  publisher_count="$(grep -Eo 'Publisher count:[[:space:]]*[0-9]+' "${ARTIFACT_DIR}/06_map_topic_info.out.log" | awk '{print $3}' | tail -n 1 || true)"
  if [[ -n "${publisher_count}" ]] && [[ "${publisher_count}" != "1" ]]; then
    step_log "FAIL: /map publisher count is ${publisher_count} (expected 1)."
    return 1
  fi

  if [[ -n "${publisher_count}" ]]; then
    step_log "PASS /map ownership: map_server with publisher_count=${publisher_count}."
  else
    step_log "WARN: could not parse /map publisher count; map_server publisher was detected."
  fi
  return 0
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
    : >"${ARTIFACT_DIR}/08_lifecycle_states.out.log"
    for n in "${nodes[@]}"; do
      local node_state_log="${ARTIFACT_DIR}/08_lifecycle_${n#/}.out.log"
      set +e
      ros2 lifecycle get "${n}" >"${node_state_log}" 2>&1
      local rc=$?
      set -e
      {
        echo ">>> ${n}"
        cat "${node_state_log}"
      } >>"${ARTIFACT_DIR}/08_lifecycle_states.out.log"
      if [[ "${rc}" -ne 0 ]]; then
        all_active=0
        continue
      fi
      if ! grep -qi "active" "${node_state_log}"; then
        all_active=0
      fi
    done

    if [[ "${all_active}" -eq 1 ]]; then
      return 0
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

  ros2 topic list >"${ARTIFACT_DIR}/06_topics_all.log" 2>/dev/null || true

  for c in "${candidates[@]}"; do
    if grep -Fxq "${c}" "${ARTIFACT_DIR}/06_topics_all.log"; then
      for qos in reliable best_effort ""; do
        set +e
        if [[ -n "${qos}" ]]; then
          timeout 8s ros2 topic echo --once "${c}" --qos-reliability "${qos}" >"${ARTIFACT_DIR}/06_lidar_probe.out.log" 2>"${ARTIFACT_DIR}/06_lidar_probe.err.log"
        else
          timeout 8s ros2 topic echo --once "${c}" >"${ARTIFACT_DIR}/06_lidar_probe.out.log" 2>"${ARTIFACT_DIR}/06_lidar_probe.err.log"
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

source_env

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
if [[ ! -f "${MAP_YAML_PATH}" ]]; then
  step_log "FAIL: map yaml missing inside container: ${MAP_YAML_PATH}"
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

if wait_tf_resolved "base_link" "${LIDAR_FRAME}" 25; then
  step_log "PASS TF resolved: base_link->${LIDAR_FRAME} (attempt ${TF_RESOLVE_MATCH_ATTEMPT})"
else
  step_log "FAIL: TF not resolvable base_link->${LIDAR_FRAME}"
  step_log "board_description log tail (last 80 lines):"
  tail -n 80 "${ARTIFACT_DIR}/01_board_description.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  tail -n 80 "${ARTIFACT_DIR}/01_board_description.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  if [[ -n "${TF_RESOLVE_LAST_OUT}" ]]; then
    step_log "tf2_echo stdout tail:"
    tail -n 80 "${TF_RESOLVE_LAST_OUT}" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  fi
  if [[ -n "${TF_RESOLVE_LAST_ERR}" ]]; then
    step_log "tf2_echo stderr tail:"
    tail -n 80 "${TF_RESOLVE_LAST_ERR}" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  fi
  exit 1
fi

if wait_tf_resolved "base_link" "${CAMERA_FRAME}" 25; then
  step_log "PASS TF resolved: base_link->${CAMERA_FRAME} (attempt ${TF_RESOLVE_MATCH_ATTEMPT})"
else
  step_log "FAIL: TF not resolvable base_link->${CAMERA_FRAME}"
  step_log "board_description log tail (last 80 lines):"
  tail -n 80 "${ARTIFACT_DIR}/01_board_description.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  tail -n 80 "${ARTIFACT_DIR}/01_board_description.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  if [[ -n "${TF_RESOLVE_LAST_OUT}" ]]; then
    step_log "tf2_echo stdout tail:"
    tail -n 80 "${TF_RESOLVE_LAST_OUT}" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  fi
  if [[ -n "${TF_RESOLVE_LAST_ERR}" ]]; then
    step_log "tf2_echo stderr tail:"
    tail -n 80 "${TF_RESOLVE_LAST_ERR}" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  fi
  exit 1
fi

if wait_tf_resolved "odom" "base_link" 25; then
  step_log "PASS TF resolved: odom->base_link (attempt ${TF_RESOLVE_MATCH_ATTEMPT})"
else
  step_log "FAIL: TF not resolvable odom->base_link"
  step_log "board_description log tail (last 80 lines):"
  tail -n 80 "${ARTIFACT_DIR}/01_board_description.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  tail -n 80 "${ARTIFACT_DIR}/01_board_description.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  if [[ -n "${TF_RESOLVE_LAST_OUT}" ]]; then
    step_log "tf2_echo stdout tail:"
    tail -n 80 "${TF_RESOLVE_LAST_OUT}" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  fi
  if [[ -n "${TF_RESOLVE_LAST_ERR}" ]]; then
    step_log "tf2_echo stderr tail:"
    tail -n 80 "${TF_RESOLVE_LAST_ERR}" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  fi
  exit 1
fi

step_log "Starting realsense launch."
REALSENSE_PID="$(start_bg \
  "ros2 launch launch/realsense_board.launch.py" \
  "${ARTIFACT_DIR}/02_realsense.out.log" \
  "${ARTIFACT_DIR}/02_realsense.err.log")"

if ! wait_realsense_ready 60; then
  fail_goal_pose_readiness "RealSense preflight failed."
fi
step_log "PASS RealSense preflight."

if ! pick_lidar_topic; then
  fail_goal_pose_readiness "LiDAR mandatory but no readable pointcloud topic found."
fi
step_log "PASS LiDAR sample read: topic=${LIDAR_PC_TOPIC_USED}"

step_log "Starting pointcloud_to_laserscan (${LIDAR_PC_TOPIC_USED} -> ${SCAN_TOPIC})."
PC2LS_PID="$(start_bg \
  "ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node --ros-args -p target_frame:=base_link -p min_height:=-0.30 -p max_height:=0.50 -p range_min:=0.10 -p range_max:=30.0 -r cloud_in:=${LIDAR_PC_TOPIC_USED} -r scan:=${SCAN_TOPIC}" \
  "${ARTIFACT_DIR}/03_pc2ls.out.log" \
  "${ARTIFACT_DIR}/03_pc2ls.err.log")"

if ! wait_scan_ready "${SCAN_TOPIC}" 20; then
  dump_scan_diagnostics "${SCAN_TOPIC}"
  fail_goal_pose_readiness "${SCAN_TOPIC} not publishing."
fi
step_log "PASS ${SCAN_TOPIC} publishing."

step_log "Starting scan_restamp (${SCAN_TOPIC} -> ${SCAN_FRESH_TOPIC})."
SCAN_RESTAMP_PID="$(start_bg \
  "python3 ${SCAN_RESTAMP_HELPER} ${SCAN_TOPIC} ${SCAN_FRESH_TOPIC}" \
  "${ARTIFACT_DIR}/04_scan_restamp.out.log" \
  "${ARTIFACT_DIR}/04_scan_restamp.err.log")"

if ! wait_scan_fresh_ready 20; then
  fail_goal_pose_readiness "${SCAN_FRESH_TOPIC} not publishing after scan_restamp start."
fi
step_log "PASS ${SCAN_FRESH_TOPIC} publishing."

step_log "Starting RTAB-Map localization."
LOCALIZATION_PID="$(start_bg \
  "ros2 launch launch/rtabmap_localization.launch.py database_path:='${DB_PATH}' rgb_topic:=${RS_RGB_TOPIC} depth_topic:=${RS_DEPTH_TOPIC} camera_info_topic:=${RS_CAMERA_INFO_TOPIC} scan_topic:=${SCAN_FRESH_TOPIC} base_frame:=base_link odom_frame:=odom map_frame:=map map_topic:=/rtabmap/map" \
  "${ARTIFACT_DIR}/05_localization.out.log" \
  "${ARTIFACT_DIR}/05_localization.err.log")"

sleep 3
if ! kill -0 "${LOCALIZATION_PID}" 2>/dev/null; then
  step_log "FAIL: RTAB-Map localization exited early."
  tail -n 120 "${ARTIFACT_DIR}/05_localization.out.log" | while IFS= read -r line; do step_log "  ${line}"; done
  tail -n 120 "${ARTIFACT_DIR}/05_localization.err.log" | while IFS= read -r line; do step_log "  ${line}"; done
  exit 1
fi
if ! wait_tf_resolved "map" "odom" 25; then
  fail_goal_pose_readiness "Localization TF not resolvable (map->odom)."
fi
if ! wait_once_topic "/rgbd_image" 12s "${ARTIFACT_DIR}/05_rgbd_image_probe.out.log" "${ARTIFACT_DIR}/05_rgbd_image_probe.err.log"; then
  fail_goal_pose_readiness "Localization input /rgbd_image not readable."
fi
if ! wait_once_topic "${SCAN_FRESH_TOPIC}" 8s "${ARTIFACT_DIR}/05_scan_fresh_probe.out.log" "${ARTIFACT_DIR}/05_scan_fresh_probe.err.log"; then
  fail_goal_pose_readiness "Localization input ${SCAN_FRESH_TOPIC} not readable after localization start."
fi
step_log "PASS localization up: process alive, map->odom TF resolvable, /rgbd_image and ${SCAN_FRESH_TOPIC} readable."

step_log "Starting Nav2 bringup (no AMCL)."
NAV2_PID="$(start_bg \
  "ros2 launch launch/nav2_rtabmap.launch.py params_file:=${NAV2_PARAMS_FILE} scan_topic:=${SCAN_FRESH_TOPIC} map_yaml:=${MAP_YAML_PATH}" \
  "${ARTIFACT_DIR}/06_nav2.out.log" \
  "${ARTIFACT_DIR}/06_nav2.err.log")"

sleep 8
if ! wait_map_ready 30; then
  fail_goal_pose_readiness "/map not received from nav2_map_server."
fi
if ! check_map_owner; then
  fail_goal_pose_readiness "/map ownership check failed."
fi
step_log "PASS nav2_map_server /map availability and ownership."

ros2 node list >"${ARTIFACT_DIR}/07_nodes_all.log" 2>/dev/null || true
for n in /map_server /controller_server /planner_server /behavior_server /bt_navigator /lifecycle_manager_navigation; do
  if ! grep -Fxq "${n}" "${ARTIFACT_DIR}/07_nodes_all.log"; then
    fail_goal_pose_readiness "Expected Nav2 node missing: ${n}"
  fi
done
step_log "PASS Nav2 nodes alive."

if ! wait_nav2_lifecycle_active 25; then
  fail_goal_pose_readiness "Nav2 lifecycle nodes did not reach active state."
fi
step_log "PASS Nav2 lifecycle states active."

ros2 action list >"${ARTIFACT_DIR}/08_actions_all.log" 2>/dev/null || true
if ! grep -Fxq "/compute_path_to_pose" "${ARTIFACT_DIR}/08_actions_all.log"; then
  fail_goal_pose_readiness "Planner interface /compute_path_to_pose not visible."
fi
if ! grep -Fxq "/follow_path" "${ARTIFACT_DIR}/08_actions_all.log"; then
  fail_goal_pose_readiness "Controller interface /follow_path not visible."
fi
step_log "PASS planner/controller action interfaces visible."

if ros2 topic type /nav2/cmd_vel >"${ARTIFACT_DIR}/09_nav2_cmd_vel_type.out.log" 2>"${ARTIFACT_DIR}/09_nav2_cmd_vel_type.err.log"; then
  step_log "PASS /nav2/cmd_vel type resolvable: $(cat "${ARTIFACT_DIR}/09_nav2_cmd_vel_type.out.log")"
else
  fail_goal_pose_readiness "/nav2/cmd_vel type not resolvable."
fi

step_log "PASS Nav2 bringup checks complete. Stack is running. Press Ctrl+C to stop."
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
  "/workspace/repo/artifacts/nav2/${TIMESTAMP}/nav2_inner.sh /workspace/repo/artifacts/nav2/${TIMESTAMP} '${container_db_path}' '${PC_TOPIC}' '${SCAN_TOPIC}' '${ALLOW_UNCALIBRATED_LIDAR}' '${LIDAR_FRAME}' '${LIDAR_XYZ}' '${LIDAR_RPY}' '${CAMERA_FRAME}' '${CAMERA_XYZ}' '${CAMERA_RPY}' '${RS_RGB_TOPIC}' '${RS_DEPTH_TOPIC}' '${RS_CAMERA_INFO_TOPIC}' '${container_map_yaml_path}'" \
  > >(tee "${RUN_DIR}/99_inner_wrapper.out.log") \
  2> >(tee "${RUN_DIR}/99_inner_wrapper.err.log" >&2)
RC=$?
set -e

if [[ ${RC} -ne 0 ]]; then
  log "FAIL: Nav2 bringup with RTAB-Map localization failed (rc=${RC})."
  log "Inspect ${RUN_DIR}/summary.log and component logs under ${RUN_DIR}."
  exit "${RC}"
fi

log "Stopped nav2 bringup stack."
