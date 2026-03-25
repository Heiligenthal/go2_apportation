#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTAINER_NAME="${CONTAINER_NAME:-go2_board_runtime}"
DURATION_SECONDS=180
REUSE_CONTAINER=1
RESTART_CONTAINER=0
LOCALIZATION_SMOKE=0
TELEOP=0
PRIVILEGED=0
EXTRINSICS_PROFILE="baseline_current"
CAMERA_TF_SOURCE="static"
LIDAR_FRAME="utlidar_lidar"
LIDAR_XYZ="0 0 0"
LIDAR_RPY="0 0 0"
CAMERA_FRAME="camera_link"
CAMERA_XYZ="0 0 0"
CAMERA_RPY="0 0 0"
ALLOW_UNCALIBRATED_LIDAR=0
SCAN_TOPIC="/scan"
PC2LS_MIN_HEIGHT="-0.30"
PC2LS_MAX_HEIGHT="0.50"
PC2LS_RANGE_MIN="0.10"
PC2LS_RANGE_MAX="30.0"

usage() {
  cat <<'USAGE'
Usage:
  scripts/rtabmap/run_r3_mapping_e2e.sh [options]

Options:
  --duration-seconds <N>   Mapping runtime window (default: 180)
  --reuse-container        Reuse running go2_board_runtime container (default)
  --restart-container      Stop running container and start a new one
  --localization-smoke     Run short localization-only smoke after mapping
  --teleop                 Print teleop inside-container hint (no auto-install)
  --privileged            Start/restart runtime container with ENABLE_PRIVILEGED=1
  --use-test-extrinsics   Load experimental mapping extrinsics from config/mapping_test_extrinsics.env
  --camera-tf-source <mode>
                          Camera TF source: static or urdf (default: static)
  --camera-frame <name>    Camera frame name expected by mapping (default: camera_link)
  --camera-xyz \"x y z\"     Camera TF translation when camera_tf_source=static
  --camera-rpy \"r p y\"     Camera TF rotation when camera_tf_source=static
  --lidar-frame <name>     LiDAR frame name expected from cloud header/TF (default: utlidar_lidar)
  --lidar-xyz \"x y z\"      Static TF translation base_link->lidar_frame (default: \"0 0 0\")
  --lidar-rpy \"r p y\"      Static TF rotation base_link->lidar_frame (default: \"0 0 0\")
  --allow-uncalibrated-lidar
                           Allow zero extrinsics \"0 0 0\" for xyz/rpy (debug only)
  --scan-topic <name>      LaserScan output topic from cloud conversion (default: /scan)
  --pc2ls-min-height <m>   pointcloud_to_laserscan min_height (default: -0.30)
  --pc2ls-max-height <m>   pointcloud_to_laserscan max_height (default: 0.50)
  --pc2ls-range-min <m>    pointcloud_to_laserscan range_min (default: 0.10)
  --pc2ls-range-max <m>    pointcloud_to_laserscan range_max (default: 30.0)
  -h, --help               Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --duration-seconds)
      if [[ $# -lt 2 ]]; then
        echo "[run_r3_mapping_e2e] ERROR: --duration-seconds requires a value." >&2
        exit 2
      fi
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
    --localization-smoke)
      LOCALIZATION_SMOKE=1
      shift
      ;;
    --teleop)
      TELEOP=1
      shift
      ;;
    --privileged)
      PRIVILEGED=1
      shift
      ;;
    --use-test-extrinsics)
      if [[ ! -f "${ROOT_DIR}/config/mapping_test_extrinsics.env" ]]; then
        echo "[run_r3_mapping_e2e] ERROR: missing config/mapping_test_extrinsics.env." >&2
        exit 1
      fi
      # shellcheck disable=SC1091
      source "${ROOT_DIR}/config/mapping_test_extrinsics.env"
      CAMERA_TF_SOURCE="${CAMERA_TF_SOURCE:-urdf}"
      EXTRINSICS_PROFILE="${EXTRINSICS_PROFILE:-test_candidate_v1}"
      shift
      ;;
    --camera-tf-source)
      [[ $# -lt 2 ]] && { echo "[run_r3_mapping_e2e] ERROR: --camera-tf-source requires a value." >&2; exit 2; }
      CAMERA_TF_SOURCE="$2"
      shift 2
      ;;
    --camera-frame)
      [[ $# -lt 2 ]] && { echo "[run_r3_mapping_e2e] ERROR: --camera-frame requires a value." >&2; exit 2; }
      CAMERA_FRAME="$2"
      shift 2
      ;;
    --camera-xyz)
      [[ $# -lt 2 ]] && { echo "[run_r3_mapping_e2e] ERROR: --camera-xyz requires a value." >&2; exit 2; }
      CAMERA_XYZ="$2"
      shift 2
      ;;
    --camera-rpy)
      [[ $# -lt 2 ]] && { echo "[run_r3_mapping_e2e] ERROR: --camera-rpy requires a value." >&2; exit 2; }
      CAMERA_RPY="$2"
      shift 2
      ;;
    --lidar-frame)
      [[ $# -lt 2 ]] && { echo "[run_r3_mapping_e2e] ERROR: --lidar-frame requires a value." >&2; exit 2; }
      LIDAR_FRAME="$2"
      shift 2
      ;;
    --lidar-xyz)
      [[ $# -lt 2 ]] && { echo "[run_r3_mapping_e2e] ERROR: --lidar-xyz requires a value." >&2; exit 2; }
      LIDAR_XYZ="$2"
      shift 2
      ;;
    --lidar-rpy)
      [[ $# -lt 2 ]] && { echo "[run_r3_mapping_e2e] ERROR: --lidar-rpy requires a value." >&2; exit 2; }
      LIDAR_RPY="$2"
      shift 2
      ;;
    --allow-uncalibrated-lidar)
      ALLOW_UNCALIBRATED_LIDAR=1
      shift
      ;;
    --scan-topic)
      [[ $# -lt 2 ]] && { echo "[run_r3_mapping_e2e] ERROR: --scan-topic requires a value." >&2; exit 2; }
      SCAN_TOPIC="$2"
      shift 2
      ;;
    --pc2ls-min-height)
      [[ $# -lt 2 ]] && { echo "[run_r3_mapping_e2e] ERROR: --pc2ls-min-height requires a value." >&2; exit 2; }
      PC2LS_MIN_HEIGHT="$2"
      shift 2
      ;;
    --pc2ls-max-height)
      [[ $# -lt 2 ]] && { echo "[run_r3_mapping_e2e] ERROR: --pc2ls-max-height requires a value." >&2; exit 2; }
      PC2LS_MAX_HEIGHT="$2"
      shift 2
      ;;
    --pc2ls-range-min)
      [[ $# -lt 2 ]] && { echo "[run_r3_mapping_e2e] ERROR: --pc2ls-range-min requires a value." >&2; exit 2; }
      PC2LS_RANGE_MIN="$2"
      shift 2
      ;;
    --pc2ls-range-max)
      [[ $# -lt 2 ]] && { echo "[run_r3_mapping_e2e] ERROR: --pc2ls-range-max requires a value." >&2; exit 2; }
      PC2LS_RANGE_MAX="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[run_r3_mapping_e2e] ERROR: unknown argument '$1'." >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! [[ "${DURATION_SECONDS}" =~ ^[0-9]+$ ]] || [[ "${DURATION_SECONDS}" -le 0 ]]; then
  echo "[run_r3_mapping_e2e] ERROR: --duration-seconds must be a positive integer." >&2
  exit 2
fi

if [[ "${CAMERA_TF_SOURCE}" != "static" && "${CAMERA_TF_SOURCE}" != "urdf" ]]; then
  echo "[run_r3_mapping_e2e] ERROR: --camera-tf-source must be 'static' or 'urdf'." >&2
  exit 2
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "[run_r3_mapping_e2e] ERROR: docker CLI not found." >&2
  exit 1
fi

if [[ ! -x "${ROOT_DIR}/scripts/bringup/run_board_runtime.sh" ]]; then
  echo "[run_r3_mapping_e2e] ERROR: scripts/bringup/run_board_runtime.sh missing or not executable." >&2
  exit 1
fi

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${ROOT_DIR}/artifacts/r3_mapping/${TIMESTAMP}"
MAP_DIR="${ROOT_DIR}/artifacts/maps/${TIMESTAMP}"
INNER_SCRIPT_HOST="${RUN_DIR}/r3_inner.sh"
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
  log "Starting runtime container '${CONTAINER_NAME}' via run_board_runtime.sh --run 'sleep infinity' (privileged=${PRIVILEGED})."
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
  runtime_launcher_pid=$!

  ready=0
  for _ in $(seq 1 30); do
    if container_running; then
      ready=1
      break
    fi
    if ! kill -0 "${runtime_launcher_pid}" 2>/dev/null; then
      break
    fi
    sleep 1
  done

  if [[ "${ready}" -ne 1 ]]; then
    log "FAIL: runtime container '${CONTAINER_NAME}' did not become ready."
    log "See ${RUN_DIR}/00_runtime_start.out.log and ${RUN_DIR}/00_runtime_start.err.log"
    exit 1
  fi

  log "Runtime container '${CONTAINER_NAME}' is running."
fi

CONTAINER_PRIVILEGED_ACTUAL="$(docker inspect -f '{{.HostConfig.Privileged}}' "${CONTAINER_NAME}" 2>/dev/null || echo "unknown")"
log "Container privilege mode: ${CONTAINER_PRIVILEGED_ACTUAL}"

cat >"${INNER_SCRIPT_HOST}" <<'INNER_EOF'
#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_DIR="$1"
MAP_DIR="$2"
DURATION_SECONDS="$3"
LOCALIZATION_SMOKE="$4"
TELEOP="$5"
LIDAR_FRAME="$6"
LIDAR_XYZ="$7"
LIDAR_RPY="$8"
ALLOW_UNCALIBRATED_LIDAR="$9"
SCAN_TOPIC="${10}"
PC2LS_MIN_HEIGHT="${11}"
PC2LS_MAX_HEIGHT="${12}"
PC2LS_RANGE_MIN="${13}"
PC2LS_RANGE_MAX="${14}"
CONTAINER_PRIVILEGED_ACTUAL="${15}"
CAMERA_FRAME="${16}"
CAMERA_XYZ="${17}"
CAMERA_RPY="${18}"
CAMERA_TF_SOURCE="${19}"
EXTRINSICS_PROFILE="${20}"
ROOT_DIR="/workspace/repo"
TOPICS_FILE="${ROOT_DIR}/config/runtime_topics.yaml"
RTABMAP_PARAMS_FILE="${ROOT_DIR}/config/rtabmap_ros2_params.yaml"
SCAN_RESTAMP_HELPER="${ROOT_DIR}/scripts/slam_toolbox/scan_restamp.py"
MAP_EVAL_HELPER="${ROOT_DIR}/scripts/rtabmap/evaluate_map_artifacts.py"
SCAN_FRESH_TOPIC="${SCAN_TOPIC%/}_fresh"

FAILURES=0
REALSENSE_PID=""
BOARD_PID=""
PC2LS_PID=""
SCAN_RESTAMP_PID=""
MAPPING_PID=""
LOCALIZATION_PID=""
DB_PATH_USED=""
LIDAR_PC_TOPIC_USED=""
LIDAR_PC_QOS_RELIABILITY_USED=""
REALSENSE_DEVICE_DETECTED=0
SCAN_PUBLISHED=0
STATIC_MAP_EXPORT_METHOD=""
MAP_YAML_PATH="${MAP_DIR}/map.yaml"
MAP_PGM_PATH="${MAP_DIR}/map.pgm"

mkdir -p "${ARTIFACT_DIR}" "${MAP_DIR}"

step_log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "${ARTIFACT_DIR}/summary.log"
}

read_yaml_value() {
  local key="$1"
  if [[ ! -f "${TOPICS_FILE}" ]]; then
    return 0
  fi
  awk -F': *' -v key="${key}" '$1 ~ "^[[:space:]]*"key"$" {print $2}' "${TOPICS_FILE}" | tr -d '"' | tail -n 1
}

is_placeholder() {
  local value="$1"
  [[ -z "${value}" || "${value}" == "<"*">" ]]
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
  local name="$1"
  local cmd="$2"
  local out_log="$3"
  local err_log="$4"

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
  stop_pid "${LOCALIZATION_PID}" "localization"
  stop_pid "${MAPPING_PID}" "mapping"
  stop_pid "${SCAN_RESTAMP_PID}" "scan_restamp"
  stop_pid "${PC2LS_PID}" "pointcloud_to_laserscan"
  stop_pid "${BOARD_PID}" "board_description"
  stop_pid "${REALSENSE_PID}" "realsense"
}
trap cleanup EXIT

source_env

preflight_rtabmap_params() {
  if [[ ! -f "${RTABMAP_PARAMS_FILE}" ]]; then
    step_log "FAIL: RTAB-Map params file not found: ${RTABMAP_PARAMS_FILE}"
    return 1
  fi

  if command -v python3 >/dev/null 2>&1; then
    if python3 - "${RTABMAP_PARAMS_FILE}" <<'PY' >"${ARTIFACT_DIR}/00_rtabmap_params_preflight.out.log" 2>"${ARTIFACT_DIR}/00_rtabmap_params_preflight.err.log"
import sys
from pathlib import Path
path = Path(sys.argv[1])
try:
    import yaml  # type: ignore
except Exception:
    print("NO_PYYAML")
    sys.exit(2)

data = yaml.safe_load(path.read_text(encoding="utf-8"))
if not isinstance(data, dict) or not data:
    print("INVALID_TOP_LEVEL")
    sys.exit(1)
for node_name, node_cfg in data.items():
    if not isinstance(node_cfg, dict) or "ros__parameters" not in node_cfg:
        print(f"MISSING_ROS_PARAMETERS:{node_name}")
        sys.exit(1)
print("VALID")
PY
    then
      step_log "PASS params preflight: ${RTABMAP_PARAMS_FILE} parsed with PyYAML."
      return 0
    fi

    # Exit code 2 means PyYAML is unavailable; use structural fallback check.
    preflight_rc=$?
    if [[ ${preflight_rc} -ne 2 ]]; then
      step_log "FAIL: RTAB-Map params parse failed. See 00_rtabmap_params_preflight.err.log"
      return 1
    fi
  fi

  if grep -qE '^[A-Za-z0-9_/]+:[[:space:]]*$' "${RTABMAP_PARAMS_FILE}" \
    && grep -qE '^[[:space:]]+ros__parameters:[[:space:]]*$' "${RTABMAP_PARAMS_FILE}"; then
    step_log "WARN: PyYAML unavailable; using structural params-file check only."
    return 0
  fi

  step_log "FAIL: RTAB-Map params file appears invalid and PyYAML is unavailable."
  return 1
}

if ! preflight_rtabmap_params; then
  exit 1
fi

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
  local attempts_dir="${ARTIFACT_DIR}/03_tf_resolve_${parent_tag}_to_${child_tag}"

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

dump_tf_secondary_diagnostics() {
  local out_file="$1"
  local err_file="$2"
  set +e
  timeout 5s ros2 topic echo --once /tf_static >"${out_file}" 2>"${err_file}"
  set -e
}

log_summary_file() {
  local header="$1"
  local file="$2"
  local max_lines="$3"
  step_log "${header}"
  if [[ ! -s "${file}" ]]; then
    step_log "  <none>"
    return 0
  fi
  sed -n "1,${max_lines}p" "${file}" | while IFS= read -r line; do
    step_log "  ${line}"
  done
}

dump_realsense_diagnostics() {
  local nodes_all="${ARTIFACT_DIR}/01_realsense_diag_nodes_all.out.log"
  local nodes_filtered="${ARTIFACT_DIR}/01_realsense_diag_nodes_filtered.out.log"
  local topics_all="${ARTIFACT_DIR}/01_realsense_diag_topics_all.out.log"
  local topics_filtered="${ARTIFACT_DIR}/01_realsense_diag_topics_filtered.out.log"
  local usb_view="${ARTIFACT_DIR}/01_realsense_diag_usb.out.log"
  local video_view="${ARTIFACT_DIR}/01_realsense_diag_video.out.log"

  set +e
  ros2 node list >"${nodes_all}" 2>"${ARTIFACT_DIR}/01_realsense_diag_nodes_all.err.log"
  grep -E 'realsense' "${nodes_all}" >"${nodes_filtered}" 2>/dev/null
  ros2 topic list >"${topics_all}" 2>"${ARTIFACT_DIR}/01_realsense_diag_topics_all.err.log"
  grep -E 'image|camera_info' "${topics_all}" >"${topics_filtered}" 2>/dev/null
  ls -l /dev/bus/usb | head -n 40 >"${usb_view}" 2>"${ARTIFACT_DIR}/01_realsense_diag_usb.err.log"
  (ls -l /dev/video* 2>/dev/null || true) >"${video_view}" 2>"${ARTIFACT_DIR}/01_realsense_diag_video.err.log"
  set -e

  log_summary_file "RealSense diag: ros2 node list | grep realsense" "${nodes_filtered}" 30
  log_summary_file "RealSense diag: ros2 topic list | grep image|camera_info" "${topics_filtered}" 60
  log_summary_file "RealSense diag: ls -l /dev/bus/usb | head" "${usb_view}" 40
  log_summary_file "RealSense diag: ls -l /dev/video*" "${video_view}" 40
}

resolve_rgb_topic_candidate() {
  local topic_list_file="$1"
  local rgb_candidate
  rgb_candidate="$(grep -E '/color/image_raw$' "${topic_list_file}" | head -n 1 || true)"
  if [[ -z "${rgb_candidate}" ]]; then
    rgb_candidate="$(grep -E '/image_raw$' "${topic_list_file}" | head -n 1 || true)"
  fi
  echo "${rgb_candidate}"
}

resolve_camera_info_topic_candidate() {
  local topic_list_file="$1"
  local camera_info_candidate
  camera_info_candidate="$(grep -E '/color/camera_info$' "${topic_list_file}" | head -n 1 || true)"
  if [[ -z "${camera_info_candidate}" ]]; then
    camera_info_candidate="$(grep -E '/camera_info$' "${topic_list_file}" | head -n 1 || true)"
  fi
  echo "${camera_info_candidate}"
}

resolve_depth_topic_candidate() {
  local topic_list_file="$1"
  local depth_candidate
  depth_candidate="$(grep -E '/aligned_depth_to_color/image_raw$' "${topic_list_file}" | head -n 1 || true)"
  echo "${depth_candidate}"
}

echo_once_topic_best_effort_fallback() {
  local topic="$1"
  local out_file="$2"
  local err_file="$3"

  set +e
  timeout 5s ros2 topic echo --once "${topic}" >"${out_file}" 2>"${err_file}"
  local rc=$?
  set -e
  if [[ ${rc} -eq 0 ]]; then
    return 0
  fi

  set +e
  if ros2 topic echo --help 2>&1 | grep -q -- '--qos-reliability'; then
    timeout 5s ros2 topic echo --once "${topic}" --qos-reliability best_effort >"${out_file}" 2>"${err_file}"
    rc=$?
  fi
  set -e

  return ${rc}
}

wait_realsense_ready() {
  local timeout_sec="$1"
  local start_ts
  local node_all_file="${ARTIFACT_DIR}/01a_realsense_node_list.out.log"
  local topic_all_file="${ARTIFACT_DIR}/01b_realsense_topic_list.out.log"
  local echo_out_file="${ARTIFACT_DIR}/01c_realsense_camera_info_echo.out.log"
  local echo_err_file="${ARTIFACT_DIR}/01c_realsense_camera_info_echo.err.log"
  start_ts="$(date +%s)"

  while true; do
    local elapsed
    elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi

    set +e
    ros2 node list >"${node_all_file}" 2>"${ARTIFACT_DIR}/01a_realsense_node_list.err.log"
    local node_rc=$?
    ros2 topic list >"${topic_all_file}" 2>"${ARTIFACT_DIR}/01b_realsense_topic_list.err.log"
    local topic_rc=$?
    set -e
    if [[ ${node_rc} -ne 0 || ${topic_rc} -ne 0 ]]; then
      sleep 1
      continue
    fi

    local node_ready=0
    if grep -Fxq "/camera/realsense2_camera" "${node_all_file}"; then
      node_ready=1
    elif grep -q "realsense2_camera" "${node_all_file}"; then
      node_ready=1
    fi
    if [[ ${node_ready} -ne 1 ]]; then
      sleep 1
      continue
    fi

    local rgb_candidate
    local depth_candidate
    local camera_info_candidate
    rgb_candidate="$(resolve_rgb_topic_candidate "${topic_all_file}")"
    depth_candidate="$(resolve_depth_topic_candidate "${topic_all_file}")"
    camera_info_candidate="$(resolve_camera_info_topic_candidate "${topic_all_file}")"

    if [[ -z "${rgb_candidate}" || -z "${depth_candidate}" || -z "${camera_info_candidate}" ]]; then
      sleep 1
      continue
    fi

    if echo_once_topic_best_effort_fallback "${camera_info_candidate}" "${echo_out_file}" "${echo_err_file}"; then
      step_log "PASS RealSense preflight: node+topics+camera_info message detected (rgb=${rgb_candidate}, depth=${depth_candidate}, camera_info=${camera_info_candidate})."
      return 0
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

if is_zero_triplet "${LIDAR_XYZ}" && is_zero_triplet "${LIDAR_RPY}" && [[ "${ALLOW_UNCALIBRATED_LIDAR}" -ne 1 ]]; then
  step_log "FAIL: LiDAR extrinsics are placeholders (lidar_xyz='${LIDAR_XYZ}', lidar_rpy='${LIDAR_RPY}')."
  step_log "Set calibrated values or use --allow-uncalibrated-lidar for debug only."
  exit 1
fi

if [[ "${ALLOW_UNCALIBRATED_LIDAR}" -eq 1 ]] && is_zero_triplet "${LIDAR_XYZ}" && is_zero_triplet "${LIDAR_RPY}"; then
  step_log "WARN: running with uncalibrated LiDAR extrinsics due to explicit override."
fi

if is_zero_triplet "${CAMERA_XYZ}" && is_zero_triplet "${CAMERA_RPY}"; then
  step_log "WARN: camera extrinsics are zero (camera_xyz='${CAMERA_XYZ}', camera_rpy='${CAMERA_RPY}')."
fi

if [[ "${CAMERA_TF_SOURCE}" == "static" ]]; then
  step_log "WARN: camera_tf_source=static while go2.urdf already contains base->camera_link. This creates a duplicate camera_link TF path during board_description bringup."
else
  step_log "INFO: camera_tf_source=urdf, so board_description will rely on robot_state_publisher for camera_link."
fi

if [[ "${TELEOP}" -eq 1 ]]; then
  if ros2 pkg executables 2>/dev/null | grep -q '^teleop_twist_keyboard '; then
    step_log "INFO: teleop requested. Start in a separate shell inside container: ros2 run teleop_twist_keyboard teleop_twist_keyboard"
  else
    step_log "INFO: teleop requested, but teleop_twist_keyboard not available. Run teleop outside container."
  fi
fi

step_log "Starting realsense launch."
REALSENSE_PID="$(start_launch_bg "realsense" "ros2 launch launch/realsense_board.launch.py" "${ARTIFACT_DIR}/01_realsense.out.log" "${ARTIFACT_DIR}/01_realsense.err.log")"

step_log "Starting board_description launch."
if [[ "${CAMERA_TF_SOURCE}" == "static" ]]; then
  CAMERA_TF_REQUIRED="true"
else
  CAMERA_TF_REQUIRED="false"
fi
BOARD_PID="$(start_launch_bg "board_description" "ros2 launch launch/board_description.launch.py lidar_tf_required:=true lidar_frame:=${LIDAR_FRAME} lidar_xyz:='${LIDAR_XYZ}' lidar_rpy:='${LIDAR_RPY}' camera_tf_required:=${CAMERA_TF_REQUIRED} camera_frame:=${CAMERA_FRAME} camera_xyz:='${CAMERA_XYZ}' camera_rpy:='${CAMERA_RPY}'" "${ARTIFACT_DIR}/02_board_description.out.log" "${ARTIFACT_DIR}/02_board_description.err.log")"

step_log "Waiting for RealSense readiness (node/topics/message, timeout 60s)."
if ! wait_realsense_ready 60; then
  step_log "FAIL: RealSense preflight failed (node/topics/message not ready within timeout)."
  step_log "Hint: if hardware is present but inaccessible, retry with --privileged and check cabling/USB power."
  dump_realsense_diagnostics
  exit 1
fi
REALSENSE_DEVICE_DETECTED=1
step_log "PASS: RealSense preflight completed."

step_log "Waiting 5s for TF/LiDAR bringup."
sleep 5

set +e
ros2 topic list >"${ARTIFACT_DIR}/03_topics_all.out.log" 2>"${ARTIFACT_DIR}/03_topics_all.err.log"
topic_list_rc=$?
set -e
if [[ ${topic_list_rc} -ne 0 ]]; then
  step_log "FAIL: unable to query ros2 topic list (rc=${topic_list_rc})."
  exit 1
fi

TOPIC_LIST_FILE="${ARTIFACT_DIR}/03_topics_all.out.log"

if ! grep -Fxq "/utlidar/cloud" "${TOPIC_LIST_FILE}" && ! grep -Fxq "/utlidar/cloud_base" "${TOPIC_LIST_FILE}"; then
  step_log "FAIL: mandatory LiDAR topics missing (/utlidar/cloud and /utlidar/cloud_base)."
  exit 1
fi

if grep -Fxq "/utlidar/cloud" "${TOPIC_LIST_FILE}"; then
  step_log "INFO: LiDAR topic /utlidar/cloud detected."
fi
if grep -Fxq "/utlidar/cloud_base" "${TOPIC_LIST_FILE}"; then
  step_log "INFO: optional LiDAR topic /utlidar/cloud_base detected."
else
  step_log "WARN: optional LiDAR topic /utlidar/cloud_base not detected."
fi

if ! lidar_read_one "${TOPIC_LIST_FILE}"; then
  step_log "FAIL: unable to read mandatory LiDAR sample from /utlidar/cloud or /utlidar/cloud_base with QoS matching."
  exit 1
fi
step_log "PASS LiDAR sample read: topic=${LIDAR_PC_TOPIC_USED} qos=${LIDAR_PC_QOS_RELIABILITY_USED}"

lidar_frame_observed="$(awk '/frame_id:/ {print $2; exit}' "${ARTIFACT_DIR}/03_lidar_cloud_sample.out.log" | tr -d '\"')"
if [[ -z "${lidar_frame_observed}" ]]; then
  step_log "FAIL: could not parse frame_id from /utlidar/cloud message."
  exit 1
fi

if [[ "${lidar_frame_observed}" != "${LIDAR_FRAME}" ]]; then
  step_log "FAIL: /utlidar/cloud frame_id='${lidar_frame_observed}' does not match expected lidar_frame='${LIDAR_FRAME}'."
  exit 1
fi
step_log "PASS LiDAR frame check: /utlidar/cloud frame_id=${lidar_frame_observed}"

if ! wait_tf_resolved "base_link" "${LIDAR_FRAME}" 25; then
  step_log "FAIL: TF not resolvable base_link->${LIDAR_FRAME}."
  step_log "board_description log tail (last 80 lines):"
  tail -n 80 "${ARTIFACT_DIR}/02_board_description.out.log" | while IFS= read -r line; do step_log "  ${line}"; done
  tail -n 80 "${ARTIFACT_DIR}/02_board_description.err.log" | while IFS= read -r line; do step_log "  ${line}"; done
  if [[ -n "${TF_RESOLVE_LAST_OUT}" ]]; then
    step_log "tf2_echo stdout tail:"
    tail -n 80 "${TF_RESOLVE_LAST_OUT}" | while IFS= read -r line; do step_log "  ${line}"; done
  fi
  if [[ -n "${TF_RESOLVE_LAST_ERR}" ]]; then
    step_log "tf2_echo stderr tail:"
    tail -n 80 "${TF_RESOLVE_LAST_ERR}" | while IFS= read -r line; do step_log "  ${line}"; done
  fi
  dump_tf_secondary_diagnostics "${ARTIFACT_DIR}/03_tf_static_secondary_lidar.out.log" "${ARTIFACT_DIR}/03_tf_static_secondary_lidar.err.log"
  step_log "Secondary diagnostics: /tf_static sample tail:"
  tail -n 40 "${ARTIFACT_DIR}/03_tf_static_secondary_lidar.out.log" | while IFS= read -r line; do step_log "  ${line}"; done
  exit 1
fi
step_log "PASS LiDAR TF check (resolvable): base_link->${LIDAR_FRAME} (attempt ${TF_RESOLVE_MATCH_ATTEMPT})"

if ! wait_tf_resolved "base_link" "${CAMERA_FRAME}" 25; then
  step_log "FAIL: TF not resolvable base_link->${CAMERA_FRAME}."
  step_log "board_description log tail (last 80 lines):"
  tail -n 80 "${ARTIFACT_DIR}/02_board_description.out.log" | while IFS= read -r line; do step_log "  ${line}"; done
  tail -n 80 "${ARTIFACT_DIR}/02_board_description.err.log" | while IFS= read -r line; do step_log "  ${line}"; done
  if [[ -n "${TF_RESOLVE_LAST_OUT}" ]]; then
    step_log "tf2_echo stdout tail:"
    tail -n 80 "${TF_RESOLVE_LAST_OUT}" | while IFS= read -r line; do step_log "  ${line}"; done
  fi
  if [[ -n "${TF_RESOLVE_LAST_ERR}" ]]; then
    step_log "tf2_echo stderr tail:"
    tail -n 80 "${TF_RESOLVE_LAST_ERR}" | while IFS= read -r line; do step_log "  ${line}"; done
  fi
  dump_tf_secondary_diagnostics "${ARTIFACT_DIR}/03_tf_static_secondary_camera.out.log" "${ARTIFACT_DIR}/03_tf_static_secondary_camera.err.log"
  step_log "Secondary diagnostics: /tf_static sample tail:"
  tail -n 40 "${ARTIFACT_DIR}/03_tf_static_secondary_camera.out.log" | while IFS= read -r line; do step_log "  ${line}"; done
  exit 1
fi
step_log "PASS camera TF check (resolvable): base_link->${CAMERA_FRAME} (attempt ${TF_RESOLVE_MATCH_ATTEMPT})"

RUNTIME_RGB="$(read_yaml_value rgb_topic)"
RUNTIME_DEPTH="$(read_yaml_value depth_topic)"
RUNTIME_CAMERA_INFO="$(read_yaml_value camera_info_topic)"
BASE_FRAME="$(read_yaml_value base_frame)"
ODOM_FRAME="$(read_yaml_value odom_frame)"
MAP_FRAME="$(read_yaml_value map_frame)"
RUNTIME_DB_PATH="$(read_yaml_value database_path)"

RGB_TOPIC=""
DEPTH_TOPIC=""
CAMERA_INFO_TOPIC=""

if ! is_placeholder "${RUNTIME_RGB}" && grep -Fxq "${RUNTIME_RGB}" "${TOPIC_LIST_FILE}"; then
  RGB_TOPIC="${RUNTIME_RGB}"
fi
if ! is_placeholder "${RUNTIME_DEPTH}" && grep -Fxq "${RUNTIME_DEPTH}" "${TOPIC_LIST_FILE}"; then
  DEPTH_TOPIC="${RUNTIME_DEPTH}"
fi
if ! is_placeholder "${RUNTIME_CAMERA_INFO}" && grep -Fxq "${RUNTIME_CAMERA_INFO}" "${TOPIC_LIST_FILE}"; then
  CAMERA_INFO_TOPIC="${RUNTIME_CAMERA_INFO}"
fi

if [[ -z "${RGB_TOPIC}" ]]; then
  RGB_TOPIC="$(grep -E '/color/image_raw$' "${TOPIC_LIST_FILE}" | head -n 1 || true)"
fi
if [[ -z "${RGB_TOPIC}" ]]; then
  RGB_TOPIC="$(grep -E '/image_raw$' "${TOPIC_LIST_FILE}" | head -n 1 || true)"
fi

if [[ -z "${CAMERA_INFO_TOPIC}" ]]; then
  CAMERA_INFO_TOPIC="$(grep -E '/color/camera_info$' "${TOPIC_LIST_FILE}" | head -n 1 || true)"
fi
if [[ -z "${CAMERA_INFO_TOPIC}" ]]; then
  CAMERA_INFO_TOPIC="$(grep -E '/camera_info$' "${TOPIC_LIST_FILE}" | head -n 1 || true)"
fi

if [[ -z "${DEPTH_TOPIC}" ]]; then
  DEPTH_TOPIC="$(grep -E '/aligned_depth_to_color/image_raw$' "${TOPIC_LIST_FILE}" | head -n 1 || true)"
fi

if [[ -z "${BASE_FRAME}" || "${BASE_FRAME}" == "<"*">" ]]; then
  BASE_FRAME="base_link"
fi
if [[ -z "${ODOM_FRAME}" || "${ODOM_FRAME}" == "<"*">" ]]; then
  ODOM_FRAME="odom"
fi
if [[ -z "${MAP_FRAME}" || "${MAP_FRAME}" == "<"*">" ]]; then
  MAP_FRAME="map"
fi

step_log "Selected topics: rgb='${RGB_TOPIC:-<none>}' depth='${DEPTH_TOPIC:-<none>}' camera_info='${CAMERA_INFO_TOPIC:-<none>}'"
step_log "Selected frames: base='${BASE_FRAME}' odom='${ODOM_FRAME}' map='${MAP_FRAME}'"

if [[ -z "${RGB_TOPIC}" || -z "${CAMERA_INFO_TOPIC}" || -z "${DEPTH_TOPIC}" ]]; then
  step_log "FAIL: could not resolve required mapping topics."
  step_log "See ${TOPIC_LIST_FILE} and scripts/rtabmap/topic_discovery_hint.sh output for candidates."
  source_env
  /workspace/repo/scripts/rtabmap/topic_discovery_hint.sh >"${ARTIFACT_DIR}/03_topic_discovery_hint.out.log" 2>"${ARTIFACT_DIR}/03_topic_discovery_hint.err.log" || true
  exit 1
fi

if ! ros2 pkg executables pointcloud_to_laserscan >/dev/null 2>&1; then
  step_log "FAIL: pointcloud_to_laserscan package/executable missing in runtime image."
  exit 1
fi

if [[ ! -f "${SCAN_RESTAMP_HELPER}" ]]; then
  step_log "FAIL: scan_restamp helper missing: ${SCAN_RESTAMP_HELPER}"
  exit 1
fi

start_pc2ls_with_input() {
  local cloud_topic="$1"
  step_log "Starting pointcloud_to_laserscan (${cloud_topic} -> ${SCAN_TOPIC})."
  PC2LS_PID="$(start_launch_bg "pointcloud_to_laserscan" "ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node --ros-args -r cloud_in:=${cloud_topic} -r scan:=${SCAN_TOPIC} -p target_frame:=base_link -p min_height:=${PC2LS_MIN_HEIGHT} -p max_height:=${PC2LS_MAX_HEIGHT} -p range_min:=${PC2LS_RANGE_MIN} -p range_max:=${PC2LS_RANGE_MAX} -p use_inf:=true" "${ARTIFACT_DIR}/03a_pointcloud_to_laserscan.out.log" "${ARTIFACT_DIR}/03a_pointcloud_to_laserscan.err.log")"
}

PC2LS_INPUT_TOPIC="${LIDAR_PC_TOPIC_USED}"
start_pc2ls_with_input "${PC2LS_INPUT_TOPIC}"

scan_ready=0
for _ in $(seq 1 15); do
  set +e
  timeout 4s ros2 topic echo --once "${SCAN_TOPIC}" >"${ARTIFACT_DIR}/03b_scan_probe.out.log" 2>"${ARTIFACT_DIR}/03b_scan_probe.err.log"
  scan_probe_rc=$?
  set -e
  if [[ ${scan_probe_rc} -eq 0 ]]; then
    scan_ready=1
    break
  fi
  sleep 1
done

if [[ ${scan_ready} -ne 1 ]]; then
  if [[ "${PC2LS_INPUT_TOPIC}" == "/utlidar/cloud" ]] && grep -Fxq "/utlidar/cloud_base" "${TOPIC_LIST_FILE}"; then
    step_log "WARN: ${SCAN_TOPIC} not publishing from /utlidar/cloud, retrying with /utlidar/cloud_base."
    stop_pid "${PC2LS_PID}" "pointcloud_to_laserscan"
    PC2LS_PID=""
    PC2LS_INPUT_TOPIC="/utlidar/cloud_base"
    start_pc2ls_with_input "${PC2LS_INPUT_TOPIC}"
    for _ in $(seq 1 15); do
      set +e
      timeout 4s ros2 topic echo --once "${SCAN_TOPIC}" >"${ARTIFACT_DIR}/03b_scan_probe.out.log" 2>"${ARTIFACT_DIR}/03b_scan_probe.err.log"
      scan_probe_rc=$?
      set -e
      if [[ ${scan_probe_rc} -eq 0 ]]; then
        scan_ready=1
        break
      fi
      sleep 1
    done
  fi
fi

if [[ ${scan_ready} -ne 1 ]]; then
  step_log "FAIL: ${SCAN_TOPIC} did not publish within timeout after pointcloud_to_laserscan start/retry."
  exit 1
fi
SCAN_PUBLISHED=1
step_log "PASS scan check: ${SCAN_TOPIC} is publishing (pc2ls_input=${PC2LS_INPUT_TOPIC})."

step_log "Starting scan_restamp (${SCAN_TOPIC} -> ${SCAN_FRESH_TOPIC})."
SCAN_RESTAMP_PID="$(start_launch_bg "scan_restamp" "python3 ${SCAN_RESTAMP_HELPER} ${SCAN_TOPIC} ${SCAN_FRESH_TOPIC}" "${ARTIFACT_DIR}/03c_scan_restamp.out.log" "${ARTIFACT_DIR}/03c_scan_restamp.err.log")"

scan_fresh_ready=0
for _ in $(seq 1 15); do
  set +e
  timeout 4s ros2 topic echo --once "${SCAN_FRESH_TOPIC}" >"${ARTIFACT_DIR}/03d_scan_fresh_probe.out.log" 2>"${ARTIFACT_DIR}/03d_scan_fresh_probe.err.log"
  scan_fresh_probe_rc=$?
  set -e
  if [[ ${scan_fresh_probe_rc} -eq 0 ]]; then
    scan_fresh_ready=1
    break
  fi
  sleep 1
done

if [[ ${scan_fresh_ready} -ne 1 ]]; then
  step_log "FAIL: ${SCAN_FRESH_TOPIC} did not publish after scan_restamp start."
  tail -n 80 "${ARTIFACT_DIR}/03c_scan_restamp.out.log" | while IFS= read -r line; do step_log "  ${line}"; done
  tail -n 80 "${ARTIFACT_DIR}/03c_scan_restamp.err.log" | while IFS= read -r line; do step_log "  ${line}"; done
  exit 1
fi
step_log "PASS scan restamp check: ${SCAN_FRESH_TOPIC} is publishing."

MANIFEST_FILE="${MAP_DIR}/manifest.txt"
{
  echo "timestamp=$(date -Iseconds)"
  echo "run_dir=${ARTIFACT_DIR}"
  echo "rgb_topic=${RGB_TOPIC}"
  echo "depth_topic=${DEPTH_TOPIC}"
  echo "camera_info_topic=${CAMERA_INFO_TOPIC}"
  echo "base_frame=${BASE_FRAME}"
  echo "odom_frame=${ODOM_FRAME}"
  echo "map_frame=${MAP_FRAME}"
  echo "lidar_frame=${LIDAR_FRAME}"
  echo "lidar_frame_observed=${lidar_frame_observed}"
  echo "lidar_xyz=${LIDAR_XYZ}"
  echo "lidar_rpy=${LIDAR_RPY}"
  echo "allow_uncalibrated_lidar=${ALLOW_UNCALIBRATED_LIDAR}"
  echo "container_privileged=${CONTAINER_PRIVILEGED_ACTUAL}"
  echo "realsense_device_detected=${REALSENSE_DEVICE_DETECTED}"
  echo "lidar_pc_topic_used=${LIDAR_PC_TOPIC_USED}"
  echo "lidar_pc_qos_reliability_used=${LIDAR_PC_QOS_RELIABILITY_USED}"
  echo "pc2ls_input_topic=${PC2LS_INPUT_TOPIC}"
  echo "scan_topic=${SCAN_TOPIC}"
  echo "scan_fresh_topic=${SCAN_FRESH_TOPIC}"
  echo "scan_published=${SCAN_PUBLISHED}"
  echo "extrinsics_profile=${EXTRINSICS_PROFILE}"
  echo "camera_tf_source=${CAMERA_TF_SOURCE}"
  echo "odom_source=/utlidar/robot_odom via go2_tf_tools odom_to_tf_broadcaster"
  echo "camera_frame=${CAMERA_FRAME}"
  echo "camera_xyz=${CAMERA_XYZ}"
  echo "camera_rpy=${CAMERA_RPY}"
  echo "pc2ls_min_height=${PC2LS_MIN_HEIGHT}"
  echo "pc2ls_max_height=${PC2LS_MAX_HEIGHT}"
  echo "pc2ls_range_min=${PC2LS_RANGE_MIN}"
  echo "pc2ls_range_max=${PC2LS_RANGE_MAX}"
  echo "duration_seconds=${DURATION_SECONDS}"
  echo "localization_smoke=${LOCALIZATION_SMOKE}"
} >"${MANIFEST_FILE}"

step_log "Starting RTAB-Map mapping for ${DURATION_SECONDS}s (scan_topic=${SCAN_FRESH_TOPIC})."
MAPPING_PID="$(start_launch_bg "mapping" "ros2 launch launch/rtabmap_mapping.launch.py rtabmap_params_file:=${RTABMAP_PARAMS_FILE} rgb_topic:=${RGB_TOPIC} depth_topic:=${DEPTH_TOPIC} camera_info_topic:=${CAMERA_INFO_TOPIC} scan_topic:=${SCAN_FRESH_TOPIC} base_frame:=${BASE_FRAME} odom_frame:=${ODOM_FRAME} map_frame:=${MAP_FRAME}" "${ARTIFACT_DIR}/03_rtabmap_mapping.out.log" "${ARTIFACT_DIR}/03_rtabmap_mapping.err.log")"

sleep "${DURATION_SECONDS}"
stop_pid "${MAPPING_PID}" "mapping"
MAPPING_PID=""

DB_PATH_CANDIDATE=""
if ! is_placeholder "${RUNTIME_DB_PATH}"; then
  DB_PATH_CANDIDATE="${RUNTIME_DB_PATH}"
fi

for candidate in "${DB_PATH_CANDIDATE}" "${HOME}/.ros/rtabmap.db" "/tmp/.ros/rtabmap.db" "/root/.ros/rtabmap.db"; do
  if [[ -n "${candidate}" && -f "${candidate}" ]]; then
    DB_PATH_USED="${candidate}"
    break
  fi
done

if [[ -n "${DB_PATH_USED}" ]]; then
  cp -a "${DB_PATH_USED}" "${MAP_DIR}/rtabmap.db"
  step_log "Saved mapping database: ${MAP_DIR}/rtabmap.db (source=${DB_PATH_USED})"
  echo "database_path_source=${DB_PATH_USED}" >>"${MANIFEST_FILE}"
else
  step_log "FAIL: no rtabmap.db found in expected locations."
  echo "database_path_source=<not_found>" >>"${MANIFEST_FILE}"
  echo "static_map_export_result=FAIL" >>"${MANIFEST_FILE}"
  echo "static_map_export_method=<not_executed_no_db>" >>"${MANIFEST_FILE}"
  FAILURES=$((FAILURES + 1))
fi

validate_mapping_db() {
  local db_file="$1"
  local mapping_log="${ARTIFACT_DIR}/03_rtabmap_mapping.out.log"
  local db_size=0
  local log_evidence=0
  local sqlite_evidence=0

  if [[ ! -f "${db_file}" ]]; then
    step_log "FAIL: mapping DB sanity check: DB file missing (${db_file})."
    return 1
  fi

  db_size="$(stat -c%s "${db_file}" 2>/dev/null || echo 0)"
  step_log "Mapping DB size: ${db_size} bytes."
  echo "database_size_bytes=${db_size}" >>"${MANIFEST_FILE}"

  if grep -Eiq 'local map=[1-9]|WM=[1-9]|map update|Added node|Registration success' "${mapping_log}"; then
    log_evidence=1
  fi
  echo "db_validation_log_evidence=${log_evidence}" >>"${MANIFEST_FILE}"

  if command -v sqlite3 >/dev/null 2>&1; then
    local sig_table=""
    sig_table="$(sqlite3 "${db_file}" "SELECT name FROM sqlite_master WHERE type='table' AND lower(name)='signatures' LIMIT 1;" 2>/dev/null || true)"
    if [[ -n "${sig_table}" ]]; then
      local sig_count=0
      sig_count="$(sqlite3 "${db_file}" "SELECT COUNT(*) FROM ${sig_table};" 2>/dev/null || echo 0)"
      if [[ "${sig_count}" =~ ^[0-9]+$ ]] && (( sig_count > 0 )); then
        sqlite_evidence=1
      fi
      echo "db_validation_signatures_count=${sig_count}" >>"${MANIFEST_FILE}"
    else
      echo "db_validation_signatures_count=<table_not_found>" >>"${MANIFEST_FILE}"
    fi
  else
    echo "db_validation_signatures_count=<sqlite3_unavailable>" >>"${MANIFEST_FILE}"
  fi
  echo "db_validation_sqlite_evidence=${sqlite_evidence}" >>"${MANIFEST_FILE}"

  if (( log_evidence == 1 || sqlite_evidence == 1 )); then
    step_log "PASS: mapping DB sanity check indicates non-empty mapping content."
    return 0
  fi

  step_log "FAIL: DB exists but appears empty/unusable for localization."
  tail -n 120 "${mapping_log}" | while IFS= read -r line; do step_log "  ${line}"; done
  return 1
}

export_static_nav_map() {
  local db_file="$1"
  local export_stdout="${ARTIFACT_DIR}/05_static_map_export.out.log"
  local export_stderr="${ARTIFACT_DIR}/05_static_map_export.err.log"
  local tmp_db="${MAP_DIR}/_reprocess_export.db"
  local tmp_pgm="${MAP_DIR}/_reprocess_export_map.pgm"
  local params_dump="${MAP_DIR}/_reprocess_export_params.ini"
  local resolution_probe_log="${ARTIFACT_DIR}/05_static_map_resolution_probe.log"
  local rtabmap_params_snippet="${ARTIFACT_DIR}/05_static_map_rtabmap_params_snippet.log"
  local nav2_params_snippet="${ARTIFACT_DIR}/05_static_map_nav2_params_snippet.log"
  local resolution=""
  local resolution_source=""

  STATIC_MAP_EXPORT_METHOD="rtabmap-reprocess+rtabmap-info"
  : >"${resolution_probe_log}"

  if ! command -v rtabmap-reprocess >/dev/null 2>&1; then
    step_log "FAIL: static map export requires rtabmap-reprocess (missing in runtime image)."
    echo "static_map_export_result=FAIL" >>"${MANIFEST_FILE}"
    echo "static_map_export_method=${STATIC_MAP_EXPORT_METHOD}" >>"${MANIFEST_FILE}"
    return 1
  fi
  if ! command -v rtabmap-info >/dev/null 2>&1; then
    step_log "FAIL: static map export requires rtabmap-info (missing in runtime image)."
    echo "static_map_export_result=FAIL" >>"${MANIFEST_FILE}"
    echo "static_map_export_method=${STATIC_MAP_EXPORT_METHOD}" >>"${MANIFEST_FILE}"
    return 1
  fi

  rm -f "${tmp_db}" "${tmp_pgm}" "${params_dump}" "${MAP_PGM_PATH}" "${MAP_YAML_PATH}"

  set +e
  rtabmap-reprocess -g2 "${db_file}" "${tmp_db}" >"${export_stdout}" 2>"${export_stderr}"
  local reprocess_rc=$?
  set -e
  if [[ ${reprocess_rc} -ne 0 ]]; then
    step_log "FAIL: static map export failed in rtabmap-reprocess (rc=${reprocess_rc})."
    echo "static_map_export_result=FAIL" >>"${MANIFEST_FILE}"
    echo "static_map_export_method=${STATIC_MAP_EXPORT_METHOD}" >>"${MANIFEST_FILE}"
    return 1
  fi

  if [[ ! -f "${tmp_pgm}" ]]; then
    step_log "FAIL: static map export did not produce PGM (${tmp_pgm})."
    echo "static_map_export_result=FAIL" >>"${MANIFEST_FILE}"
    echo "static_map_export_method=${STATIC_MAP_EXPORT_METHOD}" >>"${MANIFEST_FILE}"
    return 1
  fi

  mv -f "${tmp_pgm}" "${MAP_PGM_PATH}"

  set +e
  rtabmap-info --dump "${params_dump}" "${db_file}" >>"${export_stdout}" 2>>"${export_stderr}"
  local info_rc=$?
  set -e
  if [[ ${info_rc} -ne 0 ]]; then
    step_log "FAIL: static map export failed reading DB params via rtabmap-info (rc=${info_rc})."
    echo "static_map_export_result=FAIL" >>"${MANIFEST_FILE}"
    echo "static_map_export_method=${STATIC_MAP_EXPORT_METHOD}" >>"${MANIFEST_FILE}"
    return 1
  fi

  is_valid_resolution() {
    local value="$1"
    if [[ ! "${value}" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
      return 1
    fi
    awk -v v="${value}" 'BEGIN{exit !(v>0)}'
  }

  derive_from_db_dump() {
    local v=""
    v="$(awk -F= '
      {
        key=$1; gsub(/[[:space:]]/, "", key)
        val=$2; gsub(/^[[:space:]]+|[[:space:]]+$/, "", val)
        if (key=="Grid/CellSize" || key=="GridGlobal/CellSize") print val
      }' "${params_dump}" | tail -n 1)"
    echo "${v}"
  }

  derive_from_rtabmap_config() {
    local cfg="${RTABMAP_PARAMS_FILE}"
    local v=""
    if [[ ! -f "${cfg}" ]]; then
      echo ""
      return 0
    fi

    if command -v python3 >/dev/null 2>&1; then
      set +e
      v="$(python3 - "${cfg}" <<'PY'
import sys
from pathlib import Path
cfg = Path(sys.argv[1])
try:
    import yaml  # type: ignore
except Exception:
    print("")
    raise SystemExit(0)
try:
    data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
except Exception:
    print("")
    raise SystemExit(0)
rtab = data.get("rtabmap", {}) if isinstance(data, dict) else {}
params = rtab.get("ros__parameters", {}) if isinstance(rtab, dict) else {}
if isinstance(params, dict):
    for k in ("Grid/CellSize", "GridGlobal/CellSize"):
        if k in params and params[k] is not None:
            print(str(params[k]).strip())
            raise SystemExit(0)
print("")
PY
)"
      set -e
    fi

    if [[ -z "${v}" ]]; then
      v="$(grep -E '^[[:space:]]*(Grid/CellSize|GridGlobal/CellSize)[[:space:]]*:' "${cfg}" \
        | sed -E 's/^[^:]*:[[:space:]]*//; s/[[:space:]]+$//' | tail -n 1)"
    fi
    echo "${v}"
  }

  derive_from_nav2_config() {
    local cfg="${ROOT_DIR}/config/nav2_rtabmap_lidar_params.yaml"
    local v=""
    if [[ ! -f "${cfg}" ]]; then
      echo ""
      return 0
    fi

    if command -v python3 >/dev/null 2>&1; then
      set +e
      v="$(python3 - "${cfg}" <<'PY'
import sys
from pathlib import Path
cfg = Path(sys.argv[1])
try:
    import yaml  # type: ignore
except Exception:
    print("")
    raise SystemExit(0)
try:
    data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
except Exception:
    print("")
    raise SystemExit(0)
def pick(d):
    if not isinstance(d, dict):
        return ""
    for path in [
        ("global_costmap","global_costmap","ros__parameters","resolution"),
        ("local_costmap","local_costmap","ros__parameters","resolution"),
    ]:
        cur=d
        ok=True
        for p in path:
            if isinstance(cur, dict) and p in cur:
                cur=cur[p]
            else:
                ok=False
                break
        if ok and cur is not None:
            return str(cur).strip()
    return ""
print(pick(data))
PY
)"
      set -e
    fi

    if [[ -z "${v}" ]]; then
      v="$(grep -E '^[[:space:]]*resolution:[[:space:]]*[0-9]+([.][0-9]+)?[[:space:]]*$' "${cfg}" \
        | sed -E 's/^[^:]*:[[:space:]]*//; s/[[:space:]]+$//' | head -n 1)"
    fi
    echo "${v}"
  }

  echo "Attempt A: DB/tool dump (Grid/CellSize from ${params_dump})" >>"${resolution_probe_log}"
  resolution="$(derive_from_db_dump)"
  echo "  value='${resolution}'" >>"${resolution_probe_log}"
  if is_valid_resolution "${resolution}"; then
    resolution_source="db_tool_dump"
  else
    echo "Attempt B: RTAB-Map active config (${RTABMAP_PARAMS_FILE})" >>"${resolution_probe_log}"
    grep -nE 'Grid/CellSize|GridGlobal/CellSize|ros__parameters|rtabmap' "${RTABMAP_PARAMS_FILE}" >"${rtabmap_params_snippet}" 2>/dev/null || true
    resolution="$(derive_from_rtabmap_config)"
    echo "  value='${resolution}'" >>"${resolution_probe_log}"
    if is_valid_resolution "${resolution}"; then
      resolution_source="rtabmap_params_file"
    else
      echo "Attempt C: project fallback from nav2 config (${ROOT_DIR}/config/nav2_rtabmap_lidar_params.yaml)" >>"${resolution_probe_log}"
      grep -nE 'resolution|global_costmap|local_costmap' "${ROOT_DIR}/config/nav2_rtabmap_lidar_params.yaml" >"${nav2_params_snippet}" 2>/dev/null || true
      resolution="$(derive_from_nav2_config)"
      echo "  value='${resolution}'" >>"${resolution_probe_log}"
      if is_valid_resolution "${resolution}"; then
        resolution_source="nav2_params_fallback"
      else
        step_log "FAIL: static map export could not derive a defensible numeric resolution for map.yaml."
        step_log "Resolution attempts summary:"
        sed -n '1,120p' "${resolution_probe_log}" | while IFS= read -r line; do step_log "  ${line}"; done
        step_log "RTAB-Map tool stderr tail:"
        tail -n 80 "${export_stderr}" | while IFS= read -r line; do step_log "  ${line}"; done
        step_log "RTAB-Map tool stdout tail:"
        tail -n 80 "${export_stdout}" | while IFS= read -r line; do step_log "  ${line}"; done
        if [[ -s "${rtabmap_params_snippet}" ]]; then
          step_log "RTAB-Map config snippet:"
          sed -n '1,80p' "${rtabmap_params_snippet}" | while IFS= read -r line; do step_log "  ${line}"; done
        fi
        if [[ -s "${nav2_params_snippet}" ]]; then
          step_log "Nav2 config snippet:"
          sed -n '1,80p' "${nav2_params_snippet}" | while IFS= read -r line; do step_log "  ${line}"; done
        fi
        echo "static_map_export_result=FAIL" >>"${MANIFEST_FILE}"
        echo "static_map_export_method=${STATIC_MAP_EXPORT_METHOD}" >>"${MANIFEST_FILE}"
        echo "static_map_resolution_source=<unresolved>" >>"${MANIFEST_FILE}"
        return 1
      fi
    fi
  fi

  cat >"${MAP_YAML_PATH}" <<YAML
image: map.pgm
resolution: ${resolution}
origin: [0.0, 0.0, 0.0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.196
YAML

  if [[ ! -f "${MAP_YAML_PATH}" || ! -f "${MAP_PGM_PATH}" ]]; then
    step_log "FAIL: static map export output missing (map.yaml/map.pgm)."
    echo "static_map_export_result=FAIL" >>"${MANIFEST_FILE}"
    echo "static_map_export_method=${STATIC_MAP_EXPORT_METHOD}" >>"${MANIFEST_FILE}"
    return 1
  fi
  if ! grep -Eq '^image:[[:space:]]*map\.pgm[[:space:]]*$' "${MAP_YAML_PATH}"; then
    step_log "FAIL: map.yaml does not reference image: map.pgm."
    echo "static_map_export_result=FAIL" >>"${MANIFEST_FILE}"
    echo "static_map_export_method=${STATIC_MAP_EXPORT_METHOD}" >>"${MANIFEST_FILE}"
    return 1
  fi
  if ! grep -Eq '^resolution:[[:space:]]*[0-9]+([.][0-9]+)?[[:space:]]*$' "${MAP_YAML_PATH}"; then
    step_log "FAIL: map.yaml resolution is missing or non-numeric."
    echo "static_map_export_result=FAIL" >>"${MANIFEST_FILE}"
    echo "static_map_export_method=${STATIC_MAP_EXPORT_METHOD}" >>"${MANIFEST_FILE}"
    return 1
  fi

  rm -f "${tmp_db}" "${params_dump}"
  echo "static_map_export_result=PASS" >>"${MANIFEST_FILE}"
  echo "static_map_export_method=${STATIC_MAP_EXPORT_METHOD}" >>"${MANIFEST_FILE}"
  echo "static_map_resolution=${resolution}" >>"${MANIFEST_FILE}"
  echo "static_map_resolution_source=${resolution_source}" >>"${MANIFEST_FILE}"
  echo "map_yaml_path=${MAP_YAML_PATH}" >>"${MANIFEST_FILE}"
  echo "map_pgm_path=${MAP_PGM_PATH}" >>"${MANIFEST_FILE}"
  step_log "PASS static map export: map_yaml=${MAP_YAML_PATH}, map_pgm=${MAP_PGM_PATH}, method=${STATIC_MAP_EXPORT_METHOD}, resolution=${resolution} (${resolution_source})"
  return 0
}

if [[ -f "${MAP_DIR}/rtabmap.db" ]]; then
  if ! validate_mapping_db "${MAP_DIR}/rtabmap.db"; then
    FAILURES=$((FAILURES + 1))
  else
    if ! export_static_nav_map "${MAP_DIR}/rtabmap.db"; then
      FAILURES=$((FAILURES + 1))
    fi
  fi
fi

if [[ -x "${MAP_EVAL_HELPER}" || -f "${MAP_EVAL_HELPER}" ]]; then
  set +e
  python3 "${MAP_EVAL_HELPER}" --map-dir "${MAP_DIR}" --run-dir "${ARTIFACT_DIR}" \
    >"${ARTIFACT_DIR}/06_map_quality_eval.out.log" \
    2>"${ARTIFACT_DIR}/06_map_quality_eval.err.log"
  eval_rc=$?
  set -e
  if [[ ${eval_rc} -eq 0 ]]; then
    step_log "Map quality evaluation summary:"
    sed -n '1,40p' "${ARTIFACT_DIR}/06_map_quality_eval.out.log" | while IFS= read -r line; do step_log "  ${line}"; done
  else
    step_log "WARN: map quality evaluation helper failed (rc=${eval_rc})."
  fi
fi

if [[ "${LOCALIZATION_SMOKE}" -eq 1 ]]; then
  if [[ -f "${MAP_DIR}/rtabmap.db" ]]; then
    step_log "Starting localization smoke (~20s)."
    LOCALIZATION_PID="$(start_launch_bg "localization" "ros2 launch launch/rtabmap_localization.launch.py rtabmap_params_file:=${RTABMAP_PARAMS_FILE} rgb_topic:=${RGB_TOPIC} depth_topic:=${DEPTH_TOPIC} camera_info_topic:=${CAMERA_INFO_TOPIC} scan_topic:=${SCAN_FRESH_TOPIC} base_frame:=${BASE_FRAME} odom_frame:=${ODOM_FRAME} map_frame:=${MAP_FRAME} database_path:=${MAP_DIR}/rtabmap.db" "${ARTIFACT_DIR}/04_localization_smoke.out.log" "${ARTIFACT_DIR}/04_localization_smoke.err.log")"

    found_map_odom=0
    for _ in $(seq 1 20); do
      set +e
      timeout 3s ros2 topic echo --once /tf >"${ARTIFACT_DIR}/04_localization_tf_probe.out.log" 2>"${ARTIFACT_DIR}/04_localization_tf_probe.err.log"
      probe_rc=$?
      set -e
      if [[ ${probe_rc} -eq 0 ]]; then
        if awk '$0 ~ /frame_id:[[:space:]]*map$/ {seen=1} seen && $0 ~ /child_frame_id:[[:space:]]*odom$/ {ok=1; exit} END{exit(ok?0:1)}' "${ARTIFACT_DIR}/04_localization_tf_probe.out.log"; then
          found_map_odom=1
          break
        fi
      fi
      sleep 1
    done

    if [[ ${found_map_odom} -eq 1 ]]; then
      step_log "PASS localization smoke: map->odom detected on /tf."
    else
      step_log "FAIL localization smoke: map->odom not observed within timeout."
      FAILURES=$((FAILURES + 1))
    fi

    stop_pid "${LOCALIZATION_PID}" "localization"
    LOCALIZATION_PID=""
  else
    step_log "FAIL localization smoke requested but no DB artifact found."
    FAILURES=$((FAILURES + 1))
  fi
fi

if [[ ${FAILURES} -eq 0 ]]; then
  step_log "R3_MAPPING_E2E_RESULT=PASS"
  exit 0
fi

step_log "R3_MAPPING_E2E_RESULT=FAIL failures=${FAILURES}"
exit 1
INNER_EOF

chmod +x "${INNER_SCRIPT_HOST}"

log "Run dir: ${RUN_DIR}"
log "Map dir: ${MAP_DIR}"

set +e
docker exec "${CONTAINER_NAME}" bash -lc \
  "/workspace/repo/artifacts/r3_mapping/${TIMESTAMP}/r3_inner.sh /workspace/repo/artifacts/r3_mapping/${TIMESTAMP} /workspace/repo/artifacts/maps/${TIMESTAMP} ${DURATION_SECONDS} ${LOCALIZATION_SMOKE} ${TELEOP} '${LIDAR_FRAME}' '${LIDAR_XYZ}' '${LIDAR_RPY}' ${ALLOW_UNCALIBRATED_LIDAR} '${SCAN_TOPIC}' '${PC2LS_MIN_HEIGHT}' '${PC2LS_MAX_HEIGHT}' '${PC2LS_RANGE_MIN}' '${PC2LS_RANGE_MAX}' '${CONTAINER_PRIVILEGED_ACTUAL}' '${CAMERA_FRAME}' '${CAMERA_XYZ}' '${CAMERA_RPY}' '${CAMERA_TF_SOURCE}' '${EXTRINSICS_PROFILE}'" \
  >"${RUN_DIR}/99_inner_wrapper.out.log" \
  2>"${RUN_DIR}/99_inner_wrapper.err.log"
RC=$?
set -e

if [[ ${RC} -ne 0 ]]; then
  log "FAIL: R3 mapping E2E failed (rc=${RC})."
  log "Inspect ${RUN_DIR}/summary.log and process logs under ${RUN_DIR}."
  exit "${RC}"
fi

log "PASS: R3 mapping E2E completed."
log "Artifacts: ${MAP_DIR}"
