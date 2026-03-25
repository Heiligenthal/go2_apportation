#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTAINER_NAME="${CONTAINER_NAME:-go2_board_runtime}"
DURATION_SECONDS=180
REUSE_CONTAINER=1
RESTART_CONTAINER=0
PRIVILEGED=0
LIDAR_FRAME="utlidar_lidar"
LIDAR_XYZ="0 0 0"
LIDAR_RPY="0 0 0"
ALLOW_UNCALIBRATED_LIDAR=0
SCAN_TOPIC="/scan"
PC2LS_MIN_HEIGHT="-0.30"
PC2LS_MAX_HEIGHT="0.50"
PC2LS_RANGE_MIN="0.10"
PC2LS_RANGE_MAX="30.0"

usage() {
  cat <<'USAGE'
Usage:
  scripts/slam_toolbox/run_lidar_mapping_e2e.sh [options]

Options:
  --duration-seconds <N>     Mapping runtime in seconds (default: 180)
  --reuse-container          Reuse running go2_board_runtime container (default)
  --restart-container        Stop running container and start fresh
  --privileged               Start/restart runtime container with ENABLE_PRIVILEGED=1
  --lidar-frame <name>       Expected LiDAR frame (default: utlidar_lidar)
  --lidar-xyz "x y z"        base_link->lidar translation (default: "0 0 0")
  --lidar-rpy "r p y"        base_link->lidar rotation (default: "0 0 0")
  --allow-uncalibrated-lidar Allow zero extrinsics (debug only)
  --scan-topic <name>        LaserScan topic (default: /scan)
  --pc2ls-min-height <m>     pointcloud_to_laserscan min_height (default: -0.30)
  --pc2ls-max-height <m>     pointcloud_to_laserscan max_height (default: 0.50)
  --pc2ls-range-min <m>      pointcloud_to_laserscan range_min (default: 0.10)
  --pc2ls-range-max <m>      pointcloud_to_laserscan range_max (default: 30.0)
  -h, --help                 Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --duration-seconds)
      [[ $# -lt 2 ]] && { echo "ERROR: --duration-seconds requires value" >&2; exit 2; }
      DURATION_SECONDS="$2"
      shift 2
      ;;
    --reuse-container)
      REUSE_CONTAINER=1
      RESTART_CONTAINER=0
      shift
      ;;
    --restart-container)
      RESTART_CONTAINER=1
      REUSE_CONTAINER=0
      shift
      ;;
    --privileged)
      PRIVILEGED=1
      shift
      ;;
    --lidar-frame)
      [[ $# -lt 2 ]] && { echo "ERROR: --lidar-frame requires value" >&2; exit 2; }
      LIDAR_FRAME="$2"
      shift 2
      ;;
    --lidar-xyz)
      [[ $# -lt 2 ]] && { echo "ERROR: --lidar-xyz requires value" >&2; exit 2; }
      LIDAR_XYZ="$2"
      shift 2
      ;;
    --lidar-rpy)
      [[ $# -lt 2 ]] && { echo "ERROR: --lidar-rpy requires value" >&2; exit 2; }
      LIDAR_RPY="$2"
      shift 2
      ;;
    --allow-uncalibrated-lidar)
      ALLOW_UNCALIBRATED_LIDAR=1
      shift
      ;;
    --scan-topic)
      [[ $# -lt 2 ]] && { echo "ERROR: --scan-topic requires value" >&2; exit 2; }
      SCAN_TOPIC="$2"
      shift 2
      ;;
    --pc2ls-min-height)
      [[ $# -lt 2 ]] && { echo "ERROR: --pc2ls-min-height requires value" >&2; exit 2; }
      PC2LS_MIN_HEIGHT="$2"
      shift 2
      ;;
    --pc2ls-max-height)
      [[ $# -lt 2 ]] && { echo "ERROR: --pc2ls-max-height requires value" >&2; exit 2; }
      PC2LS_MAX_HEIGHT="$2"
      shift 2
      ;;
    --pc2ls-range-min)
      [[ $# -lt 2 ]] && { echo "ERROR: --pc2ls-range-min requires value" >&2; exit 2; }
      PC2LS_RANGE_MIN="$2"
      shift 2
      ;;
    --pc2ls-range-max)
      [[ $# -lt 2 ]] && { echo "ERROR: --pc2ls-range-max requires value" >&2; exit 2; }
      PC2LS_RANGE_MAX="$2"
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

if ! [[ "${DURATION_SECONDS}" =~ ^[0-9]+$ ]] || [[ "${DURATION_SECONDS}" -le 0 ]]; then
  echo "ERROR: --duration-seconds must be positive integer" >&2
  exit 2
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker CLI not found" >&2
  exit 1
fi

if [[ ! -x "${ROOT_DIR}/scripts/bringup/run_board_runtime.sh" ]]; then
  echo "ERROR: scripts/bringup/run_board_runtime.sh missing or not executable" >&2
  exit 1
fi

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${ROOT_DIR}/artifacts/slam_toolbox_mapping/${TIMESTAMP}"
MAP_DIR="${ROOT_DIR}/artifacts/maps/${TIMESTAMP}"
INNER_SCRIPT_HOST="${RUN_DIR}/inner.sh"
SUMMARY_LOG="${RUN_DIR}/summary.log"

mkdir -p "${RUN_DIR}" "${MAP_DIR}"

log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "${SUMMARY_LOG}"
}

container_running() {
  docker ps --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"
}

if container_running; then
  if [[ "${RESTART_CONTAINER}" -eq 1 ]]; then
    log "Stopping running container '${CONTAINER_NAME}' (--restart-container)."
    docker stop "${CONTAINER_NAME}" >>"${RUN_DIR}/00_container_manage.out.log" 2>>"${RUN_DIR}/00_container_manage.err.log"
  elif [[ "${REUSE_CONTAINER}" -eq 1 ]]; then
    log "Reusing running container '${CONTAINER_NAME}'."
  fi
fi

if ! container_running; then
  log "Starting runtime container '${CONTAINER_NAME}' (privileged=${PRIVILEGED})."
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
    log "FAIL: runtime container did not become ready."
    exit 1
  fi

  log "Runtime container '${CONTAINER_NAME}' is running."
fi

CONTAINER_PRIVILEGED_ACTUAL="$(docker inspect -f '{{.HostConfig.Privileged}}' "${CONTAINER_NAME}" 2>/dev/null || echo "unknown")"
log "Container privilege mode: ${CONTAINER_PRIVILEGED_ACTUAL}"
log "Run dir: ${RUN_DIR}"
log "Map dir: ${MAP_DIR}"

cat >"${INNER_SCRIPT_HOST}" <<'INNER_EOF'
#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_DIR="$1"
MAP_DIR="$2"
DURATION_SECONDS="$3"
LIDAR_FRAME="$4"
LIDAR_XYZ="$5"
LIDAR_RPY="$6"
ALLOW_UNCALIBRATED_LIDAR="$7"
SCAN_TOPIC="$8"
PC2LS_MIN_HEIGHT="$9"
PC2LS_MAX_HEIGHT="${10}"
PC2LS_RANGE_MIN="${11}"
PC2LS_RANGE_MAX="${12}"
CONTAINER_PRIVILEGED_ACTUAL="${13}"
ROOT_DIR="/workspace/repo"
SLAM_PARAMS_FILE="${ROOT_DIR}/config/slam_toolbox_lidar_params.yaml"
SCAN_RESTAMP_HELPER="${ROOT_DIR}/scripts/slam_toolbox/scan_restamp.py"

BOARD_PID=""
PC2LS_PID=""
SLAM_PID=""
SCAN_RESTAMP_PID=""
LIDAR_PC_TOPIC_USED=""
LIDAR_PC_QOS_RELIABILITY_USED=""
SCAN_PUBLISHED=0
SLAM_SCAN_TOPIC=""

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
  else
    step_log "WARN: install_container/setup.bash and install/setup.bash not found."
  fi

  if [[ "${restore_nounset}" -eq 1 ]]; then
    set -u
  fi
}

start_launch_bg() {
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
  if [[ -z "${pid}" ]]; then
    return
  fi
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
  stop_pid "${SLAM_PID}" "slam_toolbox"
  stop_pid "${SCAN_RESTAMP_PID}" "scan_restamp"
  stop_pid "${PC2LS_PID}" "pointcloud_to_laserscan"
  stop_pid "${BOARD_PID}" "board_description"
}
trap cleanup EXIT

normalize_triplet() {
  echo "$1" | awk '{$1=$1; print}'
}

is_zero_triplet() {
  [[ "$(normalize_triplet "$1")" == "0 0 0" ]]
}

wait_tf_static_pair() {
  local parent="$1"
  local child="$2"
  local timeout_sec="$3"
  local start_ts
  local probe_out="${ARTIFACT_DIR}/03_lidar_tf_static_probe.out.log"
  local probe_err="${ARTIFACT_DIR}/03_lidar_tf_static_probe.err.log"
  local snippet_file="${ARTIFACT_DIR}/03_lidar_tf_static_probe.filtered.log"
  start_ts="$(date +%s)"

  while true; do
    elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      if [[ -s "${probe_out}" ]]; then
        grep -E "frame_id:|child_frame_id:" "${probe_out}" >"${snippet_file}" 2>/dev/null || true
      fi
      return 1
    fi
    set +e
    timeout 3s ros2 topic echo --once /tf_static >"${probe_out}" 2>"${probe_err}"
    probe_rc=$?
    set -e
    if [[ ${probe_rc} -eq 0 ]]; then
      if awk -v p="${parent}" -v c="${child}" '
        function norm(s) { gsub(/"/, "", s); gsub(/^\//, "", s); return s }
        /frame_id:/ {
          val=$2
          val=norm(val)
          if (val==p) {
            saw_parent=1
            next
          }
        }
        /child_frame_id:/ {
          val=$2
          val=norm(val)
          if (saw_parent && val==c) {
            ok=1
            exit
          }
          saw_parent=0
        }
        END {exit(ok?0:1)}
      ' "${probe_out}"; then
        return 0
      fi
    fi
    sleep 1
  done
}

detect_topic_qos_reliability() {
  local topic="$1"
  local info_file="$2"
  set +e
  ros2 topic info -v "${topic}" >"${info_file}" 2>&1
  local rc=$?
  set -e
  if [[ ${rc} -ne 0 ]]; then
    echo "reliable"
    return 0
  fi
  local qos
  qos="$(awk '/Reliability:/{print tolower($2); exit}' "${info_file}")"
  if [[ "${qos}" == "reliable" || "${qos}" == "best_effort" ]]; then
    echo "${qos}"
  else
    echo "reliable"
  fi
}

try_lidar_topic_once() {
  local topic="$1"
  local qos="$2"
  local out_file="$3"
  local err_file="$4"
  set +e
  timeout 8s ros2 topic echo --once "${topic}" --qos-reliability "${qos}" >"${out_file}" 2>"${err_file}"
  local rc=$?
  set -e
  return ${rc}
}

lidar_read_one() {
  local topic_list_file="$1"
  local sample_out="${ARTIFACT_DIR}/03_lidar_cloud_sample.out.log"
  local sample_err="${ARTIFACT_DIR}/03_lidar_cloud_sample.err.log"
  local qos_info_file="${ARTIFACT_DIR}/03_lidar_topic_info.log"
  local topics=("/utlidar/cloud" "/utlidar/cloud_base")

  for topic in "${topics[@]}"; do
    if ! grep -Fxq "${topic}" "${topic_list_file}"; then
      continue
    fi
    local detected_qos
    detected_qos="$(detect_topic_qos_reliability "${topic}" "${qos_info_file}")"
    local qos_trials=()
    if [[ "${topic}" == "/utlidar/cloud" ]]; then
      qos_trials=("reliable" "${detected_qos}" "best_effort")
    else
      qos_trials=("${detected_qos}" "reliable" "best_effort")
    fi
    for qos in "${qos_trials[@]}"; do
      if try_lidar_topic_once "${topic}" "${qos}" "${sample_out}" "${sample_err}"; then
        LIDAR_PC_TOPIC_USED="${topic}"
        LIDAR_PC_QOS_RELIABILITY_USED="${qos}"
        return 0
      fi
    done
  done
  return 1
}

source_env

if ! ros2 pkg list | grep -qx "slam_toolbox"; then
  step_log "FAIL: slam_toolbox package missing in runtime image."
  exit 1
fi
if ! ros2 pkg executables pointcloud_to_laserscan >/dev/null 2>&1; then
  step_log "FAIL: pointcloud_to_laserscan missing in runtime image."
  exit 1
fi
if [[ ! -f "${SCAN_RESTAMP_HELPER}" ]]; then
  step_log "FAIL: scan restamp helper not found: ${SCAN_RESTAMP_HELPER}"
  exit 1
fi

dump_slam_observability() {
  set +e
  ros2 node list >"${ARTIFACT_DIR}/06_slam_node_list_all.out.log" 2>"${ARTIFACT_DIR}/06_slam_node_list_all.err.log"
  grep -E "slam" "${ARTIFACT_DIR}/06_slam_node_list_all.out.log" >"${ARTIFACT_DIR}/06_slam_node_list_filtered.out.log" 2>/dev/null
  for p in publish_tf map_frame odom_frame base_frame scan_topic use_odometry transform_publish_period; do
    ros2 param get /slam_toolbox "${p}" >"${ARTIFACT_DIR}/06_slam_param_${p}.out.log" 2>"${ARTIFACT_DIR}/06_slam_param_${p}.err.log" || \
      ros2 param get slam_toolbox "${p}" >"${ARTIFACT_DIR}/06_slam_param_${p}.out.log" 2>"${ARTIFACT_DIR}/06_slam_param_${p}.err.log" || true
  done
  set -e

  step_log "slam diag: ros2 node list | grep slam"
  if [[ -s "${ARTIFACT_DIR}/06_slam_node_list_filtered.out.log" ]]; then
    while IFS= read -r line; do
      step_log "  ${line}"
    done < "${ARTIFACT_DIR}/06_slam_node_list_filtered.out.log"
  else
    step_log "  <none>"
  fi

  for p in publish_tf map_frame odom_frame base_frame scan_topic use_odometry transform_publish_period; do
    step_log "slam diag: param ${p}"
    if [[ -s "${ARTIFACT_DIR}/06_slam_param_${p}.out.log" ]]; then
      while IFS= read -r line; do
        step_log "  ${line}"
      done < "${ARTIFACT_DIR}/06_slam_param_${p}.out.log"
    else
      step_log "  <unavailable>"
    fi
  done

  step_log "slam diag: last 80 lines from 05_slam_toolbox.out.log"
  if [[ -s "${ARTIFACT_DIR}/05_slam_toolbox.out.log" ]]; then
    tail -n 80 "${ARTIFACT_DIR}/05_slam_toolbox.out.log" >"${ARTIFACT_DIR}/06_slam_tail80.out.log" || true
    while IFS= read -r line; do
      step_log "  ${line}"
    done < "${ARTIFACT_DIR}/06_slam_tail80.out.log"
  else
    step_log "  <no slam output log>"
  fi
}

if is_zero_triplet "${LIDAR_XYZ}" && is_zero_triplet "${LIDAR_RPY}" && [[ "${ALLOW_UNCALIBRATED_LIDAR}" -ne 1 ]]; then
  step_log "FAIL: LiDAR extrinsics are placeholders. Set lidar_xyz/lidar_rpy or use --allow-uncalibrated-lidar."
  exit 1
fi
if [[ "${ALLOW_UNCALIBRATED_LIDAR}" -eq 1 ]] && is_zero_triplet "${LIDAR_XYZ}" && is_zero_triplet "${LIDAR_RPY}"; then
  step_log "WARN: running with uncalibrated LiDAR extrinsics due to explicit override."
fi

step_log "Starting board_description launch."
BOARD_PID="$(start_launch_bg "ros2 launch launch/board_description.launch.py lidar_tf_required:=true lidar_frame:=${LIDAR_FRAME} lidar_xyz:='${LIDAR_XYZ}' lidar_rpy:='${LIDAR_RPY}'" "${ARTIFACT_DIR}/01_board_description.out.log" "${ARTIFACT_DIR}/01_board_description.err.log")"
sleep 5

set +e
ros2 topic list >"${ARTIFACT_DIR}/02_topics_all.out.log" 2>"${ARTIFACT_DIR}/02_topics_all.err.log"
topic_list_rc=$?
set -e
if [[ ${topic_list_rc} -ne 0 ]]; then
  step_log "FAIL: unable to run ros2 topic list."
  exit 1
fi

TOPIC_LIST_FILE="${ARTIFACT_DIR}/02_topics_all.out.log"
if ! grep -Fxq "/utlidar/cloud" "${TOPIC_LIST_FILE}" && ! grep -Fxq "/utlidar/cloud_base" "${TOPIC_LIST_FILE}"; then
  step_log "FAIL: mandatory LiDAR topics missing (/utlidar/cloud and /utlidar/cloud_base)."
  exit 1
fi

if ! lidar_read_one "${TOPIC_LIST_FILE}"; then
  step_log "FAIL: unable to read LiDAR sample from /utlidar/cloud or /utlidar/cloud_base."
  exit 1
fi
step_log "PASS LiDAR sample read: topic=${LIDAR_PC_TOPIC_USED} qos=${LIDAR_PC_QOS_RELIABILITY_USED}"

lidar_frame_observed="$(awk '/frame_id:/ {print $2; exit}' "${ARTIFACT_DIR}/03_lidar_cloud_sample.out.log" | tr -d '\"')"
if [[ -z "${lidar_frame_observed}" || "${lidar_frame_observed}" != "${LIDAR_FRAME}" ]]; then
  step_log "FAIL: observed LiDAR frame '${lidar_frame_observed:-<none>}' does not match expected '${LIDAR_FRAME}'."
  exit 1
fi
step_log "PASS LiDAR frame check: ${lidar_frame_observed}"

if ! wait_tf_static_pair "base_link" "${LIDAR_FRAME}" 25; then
  step_log "FAIL: TF static pair base_link->${LIDAR_FRAME} not observed."
  step_log "TF static snippet (frame_id/child_frame_id):"
  if [[ -s "${ARTIFACT_DIR}/03_lidar_tf_static_probe.filtered.log" ]]; then
    while IFS= read -r line; do
      step_log "  ${line}"
    done < "${ARTIFACT_DIR}/03_lidar_tf_static_probe.filtered.log"
  else
    step_log "  <no filtered tf_static snippet>"
  fi
  step_log "Last 60 lines of board_description log:"
  if [[ -s "${ARTIFACT_DIR}/01_board_description.out.log" ]]; then
    tail -n 60 "${ARTIFACT_DIR}/01_board_description.out.log" >"${ARTIFACT_DIR}/03_board_description_tail60.log" || true
    while IFS= read -r line; do
      step_log "  ${line}"
    done < "${ARTIFACT_DIR}/03_board_description_tail60.log"
  else
    step_log "  <no board_description output log>"
  fi
  exit 1
fi
step_log "PASS LiDAR TF check: base_link->${LIDAR_FRAME}"

step_log "Starting pointcloud_to_laserscan (${LIDAR_PC_TOPIC_USED} -> ${SCAN_TOPIC})."
PC2LS_PID="$(start_launch_bg \
  "ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node --ros-args -r cloud_in:=${LIDAR_PC_TOPIC_USED} -r scan:=${SCAN_TOPIC} -p target_frame:=base_link -p min_height:=${PC2LS_MIN_HEIGHT} -p max_height:=${PC2LS_MAX_HEIGHT} -p range_min:=${PC2LS_RANGE_MIN} -p range_max:=${PC2LS_RANGE_MAX} -p use_inf:=true" \
  "${ARTIFACT_DIR}/03_pc2ls.out.log" \
  "${ARTIFACT_DIR}/03_pc2ls.err.log")"

scan_ready=0
for _ in $(seq 1 15); do
  set +e
  timeout 4s ros2 topic echo --once "${SCAN_TOPIC}" >"${ARTIFACT_DIR}/04_scan_probe.out.log" 2>"${ARTIFACT_DIR}/04_scan_probe.err.log"
  scan_rc=$?
  set -e
  if [[ ${scan_rc} -eq 0 ]]; then
    scan_ready=1
    break
  fi
  sleep 1
done
if [[ ${scan_ready} -ne 1 ]]; then
  step_log "FAIL: ${SCAN_TOPIC} did not publish after pointcloud_to_laserscan start."
  exit 1
fi
SCAN_PUBLISHED=1
step_log "PASS scan check: ${SCAN_TOPIC} is publishing."

SLAM_SCAN_TOPIC="${SCAN_TOPIC}_fresh"
step_log "Starting scan restamp helper (${SCAN_TOPIC} -> ${SLAM_SCAN_TOPIC})."
SCAN_RESTAMP_PID="$(start_launch_bg \
  "python3 ${SCAN_RESTAMP_HELPER} '${SCAN_TOPIC}' '${SLAM_SCAN_TOPIC}'" \
  "${ARTIFACT_DIR}/04_scan_restamp.out.log" \
  "${ARTIFACT_DIR}/04_scan_restamp.err.log")"

fresh_scan_ready=0
scan_echo_supports_qos=0
if ros2 topic echo --help 2>&1 | grep -q -- '--qos-reliability'; then
  scan_echo_supports_qos=1
fi
for _ in $(seq 1 15); do
  set +e
  if [[ ${scan_echo_supports_qos} -eq 1 ]]; then
    timeout 4s ros2 topic echo --once "${SLAM_SCAN_TOPIC}" --qos-reliability best_effort >"${ARTIFACT_DIR}/04_scan_fresh_probe.out.log" 2>"${ARTIFACT_DIR}/04_scan_fresh_probe.err.log"
    fresh_scan_rc=$?
  else
    timeout 4s ros2 topic echo --once "${SLAM_SCAN_TOPIC}" >"${ARTIFACT_DIR}/04_scan_fresh_probe.out.log" 2>"${ARTIFACT_DIR}/04_scan_fresh_probe.err.log"
    fresh_scan_rc=$?
  fi
  set -e
  if [[ ${fresh_scan_rc} -eq 0 ]]; then
    fresh_scan_ready=1
    break
  fi
  sleep 1
done
if [[ ${fresh_scan_ready} -ne 1 ]]; then
  step_log "FAIL: ${SLAM_SCAN_TOPIC} did not publish after scan restamp start."
  step_log "scan_restamp log tail (last 80 lines):"
  if [[ -s "${ARTIFACT_DIR}/04_scan_restamp.out.log" ]]; then
    tail -n 80 "${ARTIFACT_DIR}/04_scan_restamp.out.log" >"${ARTIFACT_DIR}/04_scan_restamp_tail80.out.log" || true
    while IFS= read -r line; do
      step_log "  ${line}"
    done < "${ARTIFACT_DIR}/04_scan_restamp_tail80.out.log"
  else
    step_log "  <no scan_restamp stdout log>"
  fi
  exit 1
fi
step_log "PASS scan restamp check: ${SLAM_SCAN_TOPIC} is publishing."

step_log "Starting slam_toolbox mapping launch."
SLAM_PID="$(start_launch_bg \
  "ros2 launch launch/slam_toolbox_lidar.launch.py slam_params_file:=${SLAM_PARAMS_FILE} scan_topic:=${SLAM_SCAN_TOPIC} base_frame:=base_link odom_frame:=odom map_frame:=map" \
  "${ARTIFACT_DIR}/05_slam_toolbox.out.log" \
  "${ARTIFACT_DIR}/05_slam_toolbox.err.log")"

sleep 5
map_odom_seen=0
for _ in $(seq 1 20); do
  set +e
  timeout 3s ros2 topic echo --once /tf >"${ARTIFACT_DIR}/06_tf_probe.out.log" 2>"${ARTIFACT_DIR}/06_tf_probe.err.log"
  tf_rc=$?
  set -e
  if [[ ${tf_rc} -eq 0 ]]; then
    if awk '$0 ~ /frame_id:[[:space:]]*map$/ {seen=1} seen && $0 ~ /child_frame_id:[[:space:]]*odom$/ {ok=1; exit} END{exit(ok?0:1)}' "${ARTIFACT_DIR}/06_tf_probe.out.log"; then
      map_odom_seen=1
      break
    fi
  fi
  sleep 1
done
if [[ ${map_odom_seen} -ne 1 ]]; then
  step_log "FAIL: map->odom not observed on /tf while slam_toolbox is running."
  dump_slam_observability
  exit 1
fi
step_log "PASS localization smoke: map->odom observed on /tf."

step_log "Mapping window: ${DURATION_SECONDS}s."
sleep "${DURATION_SECONDS}"

MAP_PREFIX="${MAP_DIR}/map"
map_saved=0
if ros2 service list | grep -Fxq "/slam_toolbox/save_map"; then
  set +e
  ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: '${MAP_PREFIX}'}}" \
    >"${ARTIFACT_DIR}/07_save_map_service.out.log" \
    2>"${ARTIFACT_DIR}/07_save_map_service.err.log"
  save_rc=$?
  set -e
  if [[ ${save_rc} -eq 0 ]] && [[ -f "${MAP_PREFIX}.pgm" ]] && [[ -f "${MAP_PREFIX}.yaml" ]]; then
    map_saved=1
  fi
fi

if [[ ${map_saved} -ne 1 ]] && ros2 pkg executables nav2_map_server 2>/dev/null | grep -q "map_saver_cli"; then
  set +e
  ros2 run nav2_map_server map_saver_cli -f "${MAP_PREFIX}" --ros-args -r map:=/map \
    >"${ARTIFACT_DIR}/07_map_saver_cli.out.log" \
    2>"${ARTIFACT_DIR}/07_map_saver_cli.err.log"
  save_cli_rc=$?
  set -e
  if [[ ${save_cli_rc} -eq 0 ]] && [[ -f "${MAP_PREFIX}.pgm" ]] && [[ -f "${MAP_PREFIX}.yaml" ]]; then
    map_saved=1
  fi
fi

if [[ ${map_saved} -ne 1 ]]; then
  step_log "FAIL: map export failed (expected ${MAP_PREFIX}.pgm and ${MAP_PREFIX}.yaml)."
  step_log "Try installing nav2_map_server or verify /slam_toolbox/save_map service behavior."
  exit 1
fi
step_log "PASS map export: ${MAP_PREFIX}.pgm + ${MAP_PREFIX}.yaml"

MANIFEST_FILE="${MAP_DIR}/manifest.txt"
{
  echo "timestamp=$(date -Iseconds)"
  echo "container_privileged=${CONTAINER_PRIVILEGED_ACTUAL}"
  echo "lidar_frame=${LIDAR_FRAME}"
  echo "lidar_frame_observed=${lidar_frame_observed}"
  echo "lidar_xyz=${LIDAR_XYZ}"
  echo "lidar_rpy=${LIDAR_RPY}"
  echo "allow_uncalibrated_lidar=${ALLOW_UNCALIBRATED_LIDAR}"
  echo "lidar_pc_topic_used=${LIDAR_PC_TOPIC_USED}"
  echo "lidar_pc_qos_reliability_used=${LIDAR_PC_QOS_RELIABILITY_USED}"
  echo "scan_topic_raw=${SCAN_TOPIC}"
  echo "scan_topic_slam=${SLAM_SCAN_TOPIC}"
  echo "scan_published=${SCAN_PUBLISHED}"
  echo "slam_params_file=${SLAM_PARAMS_FILE}"
  echo "map_export_prefix=${MAP_PREFIX}"
  echo "duration_seconds=${DURATION_SECONDS}"
} >"${MANIFEST_FILE}"

step_log "LIDAR_MAPPING_E2E_RESULT=PASS"
exit 0
INNER_EOF

chmod +x "${INNER_SCRIPT_HOST}"

set +e
docker exec "${CONTAINER_NAME}" bash -lc \
  "/workspace/repo/artifacts/slam_toolbox_mapping/${TIMESTAMP}/inner.sh /workspace/repo/artifacts/slam_toolbox_mapping/${TIMESTAMP} /workspace/repo/artifacts/maps/${TIMESTAMP} ${DURATION_SECONDS} '${LIDAR_FRAME}' '${LIDAR_XYZ}' '${LIDAR_RPY}' ${ALLOW_UNCALIBRATED_LIDAR} '${SCAN_TOPIC}' '${PC2LS_MIN_HEIGHT}' '${PC2LS_MAX_HEIGHT}' '${PC2LS_RANGE_MIN}' '${PC2LS_RANGE_MAX}' '${CONTAINER_PRIVILEGED_ACTUAL}'" \
  >"${RUN_DIR}/99_inner_wrapper.out.log" \
  2>"${RUN_DIR}/99_inner_wrapper.err.log"
RC=$?
set -e

if [[ ${RC} -ne 0 ]]; then
  log "FAIL: LiDAR-only slam_toolbox mapping E2E failed (rc=${RC})."
  log "Inspect ${RUN_DIR}/summary.log and logs under ${RUN_DIR}."
  exit "${RC}"
fi

log "PASS: LiDAR-only slam_toolbox mapping E2E completed."
log "Artifacts: ${MAP_DIR}"
