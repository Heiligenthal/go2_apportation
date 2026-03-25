#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTAINER_NAME="${CONTAINER_NAME:-go2_board_runtime}"
DB_PATH=""
RESTART_CONTAINER=0
PRIVILEGED=0
ALLOW_UNCALIBRATED_LIDAR=0
PC_TOPIC=""
SCAN_TOPIC="/scan"
EXTRINSICS_ENV_PATH=""
CAMERA_XYZ_ENV_SET="${CAMERA_XYZ+x}"
CAMERA_RPY_ENV_SET="${CAMERA_RPY+x}"
LIDAR_FRAME="utlidar_lidar"
LIDAR_XYZ="0 0 0"
LIDAR_RPY="0 0 0"
CAMERA_FRAME="${CAMERA_FRAME:-camera_link}"
CAMERA_XYZ="${CAMERA_XYZ:-0 0 0}"
CAMERA_RPY="${CAMERA_RPY:-0 0 0}"

RS_RGB_TOPIC="/camera/realsense2_camera/color/image_raw"
RS_DEPTH_TOPIC="/camera/realsense2_camera/aligned_depth_to_color/image_raw"
RS_CAMERA_INFO_TOPIC="/camera/realsense2_camera/color/camera_info"

usage() {
  cat <<'USAGE'
Usage:
  scripts/rtabmap/run_r3_localization_visualize.sh [options]

Options:
  --db <path>                    RTAB-Map DB path (default: latest artifacts/maps/*/rtabmap.db)
  --restart-container            Stop running container and start fresh
  --privileged                   Start/restart runtime container with ENABLE_PRIVILEGED=1
  --allow-uncalibrated-lidar     Allow lidar_xyz/lidar_rpy both "0 0 0" (debug only)
  --extrinsics-env <path>        Explicit camera-mount best_extrinsics.env (default: latest calibration run)
  --pc-topic <topic>             PointCloud2 input (default: prefer /utlidar/cloud then /utlidar/cloud_base)
  --scan-topic <topic>           LaserScan output topic (default: /scan)
  -h, --help                     Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --db)
      [[ $# -lt 2 ]] && { echo "[run_r3_localization_visualize] ERROR: --db requires a value." >&2; exit 2; }
      DB_PATH="$2"
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
    --extrinsics-env)
      [[ $# -lt 2 ]] && { echo "[run_r3_localization_visualize] ERROR: --extrinsics-env requires a value." >&2; exit 2; }
      EXTRINSICS_ENV_PATH="$2"
      shift 2
      ;;
    --pc-topic)
      [[ $# -lt 2 ]] && { echo "[run_r3_localization_visualize] ERROR: --pc-topic requires a value." >&2; exit 2; }
      PC_TOPIC="$2"
      shift 2
      ;;
    --scan-topic)
      [[ $# -lt 2 ]] && { echo "[run_r3_localization_visualize] ERROR: --scan-topic requires a value." >&2; exit 2; }
      SCAN_TOPIC="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[run_r3_localization_visualize] ERROR: unknown argument '$1'." >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "[run_r3_localization_visualize] ERROR: docker CLI not found." >&2
  exit 1
fi

if [[ ! -x "${ROOT_DIR}/scripts/bringup/run_board_runtime.sh" ]]; then
  echo "[run_r3_localization_visualize] ERROR: scripts/bringup/run_board_runtime.sh missing or not executable." >&2
  exit 1
fi

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${ROOT_DIR}/artifacts/rtabmap_localization/${TIMESTAMP}"
INNER_SCRIPT_HOST="${RUN_DIR}/localization_inner.sh"
SUMMARY_LOG="${RUN_DIR}/summary.log"

mkdir -p "${RUN_DIR}"

log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "${SUMMARY_LOG}"
}

container_running() {
  docker ps --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"
}

latest_db() {
  local latest_dir
  latest_dir="$(ls -1d "${ROOT_DIR}/artifacts/maps"/* 2>/dev/null | sort | tail -n 1 || true)"
  if [[ -z "${latest_dir}" ]]; then
    return 1
  fi
  if [[ -f "${latest_dir}/rtabmap.db" ]]; then
    echo "${latest_dir}/rtabmap.db"
    return 0
  fi
  return 1
}

resolve_path() {
  local path_value="$1"
  if [[ "${path_value}" = /* ]]; then
    printf '%s\n' "${path_value}"
  else
    printf '%s\n' "${ROOT_DIR}/${path_value}"
  fi
}

latest_calibration_dir() {
  local calibration_root latest_link resolved
  calibration_root="${ROOT_DIR}/artifacts/calibration/camera_mount"
  latest_link="${calibration_root}/latest"
  if [[ -L "${latest_link}" ]]; then
    resolved="$(cd "$(dirname "${latest_link}")" && readlink "${latest_link}")"
    if [[ -n "${resolved}" && -d "${calibration_root}/${resolved}" ]]; then
      printf '%s\n' "${calibration_root}/${resolved}"
      return 0
    fi
  fi

  find "${calibration_root}" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' 2>/dev/null \
    | sort -nr \
    | awk '{print $2}' \
    | while IFS= read -r run_dir; do
        [[ -f "${run_dir}/best_extrinsics.env" ]] || continue
        printf '%s\n' "${run_dir}"
        break
      done
}

load_camera_mount_calibration_if_needed() {
  local calibration_dir extrinsics_env calibration_snapshot
  if [[ -n "${CAMERA_XYZ_ENV_SET}" && -n "${CAMERA_RPY_ENV_SET}" ]]; then
    log "Using CAMERA_XYZ/CAMERA_RPY from environment: camera_xyz='${CAMERA_XYZ}' camera_rpy='${CAMERA_RPY}'"
    return 0
  fi

  extrinsics_env=""
  if [[ -n "${EXTRINSICS_ENV_PATH}" ]]; then
    extrinsics_env="$(resolve_path "${EXTRINSICS_ENV_PATH}")"
  else
    calibration_dir="$(latest_calibration_dir || true)"
    if [[ -n "${calibration_dir}" ]]; then
      extrinsics_env="${calibration_dir}/best_extrinsics.env"
    fi
  fi

  if [[ -z "${extrinsics_env}" || ! -f "${extrinsics_env}" ]]; then
    log "No camera mount calibration found; using camera_xyz/camera_rpy as currently set"
    return 0
  fi

  calibration_snapshot="${RUN_DIR}/00_camera_mount_calibration.env"
  python3 - "${extrinsics_env}" "${calibration_snapshot}" <<'PY'
import shlex
import sys
from pathlib import Path

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
values = {}
for raw_line in src.read_text(encoding="utf-8").splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    values[key.strip()] = value.strip()

required = ["X", "Y", "Z", "ROLL_DEG", "PITCH_DEG", "YAW_DEG"]
missing = [key for key in required if key not in values or values[key] == ""]
if missing:
    raise SystemExit(f"best_extrinsics.env missing required keys: {', '.join(missing)}")

camera_xyz = f"{values['X']} {values['Y']} {values['Z']}"
camera_rpy = f"{values['ROLL_DEG']} {values['PITCH_DEG']} {values['YAW_DEG']}"
dst.write_text(
    "CAMERA_XYZ=" + shlex.quote(camera_xyz) + "\n"
    + "CAMERA_RPY=" + shlex.quote(camera_rpy) + "\n",
    encoding="utf-8",
)
PY

  # shellcheck disable=SC1090
  source "${calibration_snapshot}"
  log "Loaded camera mount calibration from ${extrinsics_env}: camera_xyz='${CAMERA_XYZ}' camera_rpy='${CAMERA_RPY}'"
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

container_db_path="${host_db_path}"
if [[ "${host_db_path}" == "${ROOT_DIR}"/* ]]; then
  container_db_path="/workspace/repo/${host_db_path#${ROOT_DIR}/}"
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
    log "FAIL: runtime container '${CONTAINER_NAME}' did not become ready."
    log "Inspect ${RUN_DIR}/00_runtime_start.err.log"
    exit 1
  fi

  log "Runtime container '${CONTAINER_NAME}' is running."
else
  log "Reusing running container '${CONTAINER_NAME}'."
fi

CONTAINER_PRIVILEGED_ACTUAL="$(docker inspect -f '{{.HostConfig.Privileged}}' "${CONTAINER_NAME}" 2>/dev/null || echo "unknown")"
log "Container privilege mode: ${CONTAINER_PRIVILEGED_ACTUAL}"
log "Run dir: ${RUN_DIR}"
log "RTAB-Map DB: ${host_db_path}"
load_camera_mount_calibration_if_needed

cat >"${INNER_SCRIPT_HOST}" <<'INNER_EOF'
#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_DIR="$1"
DB_PATH="$2"
PC_TOPIC_REQUESTED="$3"
SCAN_TOPIC="$4"
LIDAR_FRAME="$5"
LIDAR_XYZ="$6"
LIDAR_RPY="$7"
ALLOW_UNCALIBRATED_LIDAR="$8"
CAMERA_FRAME="$9"
CAMERA_XYZ="${10}"
CAMERA_RPY="${11}"
ROOT_DIR="/workspace/repo"

BOARD_PID=""
REALSENSE_PID=""
PC2LS_PID=""
SCAN_RESTAMP_PID=""
LOCALIZATION_PID=""
LIDAR_PC_TOPIC_USED=""
LIDAR_PC_QOS_USED=""
SCAN_FRESH_TOPIC="${SCAN_TOPIC%/}_fresh"
SCAN_RESTAMP_HELPER="${ROOT_DIR}/scripts/slam_toolbox/scan_restamp.py"

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
  else
    step_log "WARN: install_container/setup.bash and install/setup.bash not found."
  fi

  if [[ "${restore_nounset}" -eq 1 ]]; then
    set -u
  fi
}

strip_tf_value() {
  local v="$1"
  v="${v//\"/}"
  v="${v#"${v%%[![:space:]]*}"}"
  v="${v%"${v##*[![:space:]]}"}"
  v="${v#/}"
  echo "${v}"
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

wait_tf_static_pair() {
  local parent="$1"
  local child="$2"
  local timeout_sec="$3"
  local start_ts="$(date +%s)"
  local samples_dir="${ARTIFACT_DIR}/02_tf_static_samples"
  local all_pairs_log="${ARTIFACT_DIR}/02_tf_static_pairs.log"
  local norm_parent norm_child
  local attempt=0
  TF_STATIC_MATCH_ATTEMPT=""
  mkdir -p "${samples_dir}"
  : >"${all_pairs_log}"
  norm_parent="$(echo "${parent}" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g; s#^/+##; s/"//g')"
  norm_child="$(echo "${child}" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g; s#^/+##; s/"//g')"

  while true; do
    local elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi

    attempt=$((attempt + 1))
    local out_log="${samples_dir}/attempt_${attempt}.out.log"
    local err_log="${samples_dir}/attempt_${attempt}.err.log"
    local pairs_log="${samples_dir}/attempt_${attempt}.pairs.log"
    set +e
    timeout 5s ros2 topic echo --once /tf_static >"${out_log}" 2>"${err_log}"
    local rc=$?
    set -e

    if [[ "${rc}" -eq 0 ]]; then
      awk '
        function norm(v) {
          gsub(/^[[:space:]]+|[[:space:]]+$/, "", v)
          gsub(/"/, "", v)
          sub(/^\/+/, "", v)
          return v
        }
        function emit_pair() {
          if (current_frame != "" && current_child != "") {
            print current_frame " -> " current_child
            current_frame = ""
            current_child = ""
          }
        }
        /^[[:space:]]*-[[:space:]]*header:[[:space:]]*$/ {
          emit_pair()
          next
        }
        /^[[:space:]]*frame_id:[[:space:]]*/ {
          v = $0
          sub(/^[^:]*:[[:space:]]*/, "", v)
          current_frame = norm(v)
          next
        }
        /^[[:space:]]*child_frame_id:[[:space:]]*/ {
          v = $0
          sub(/^[^:]*:[[:space:]]*/, "", v)
          current_child = norm(v)
          emit_pair()
          next
        }
        END {
          emit_pair()
        }
      ' "${out_log}" >"${pairs_log}" || true

      {
        echo "attempt ${attempt}:"
        cat "${pairs_log}" 2>/dev/null || true
      } >>"${all_pairs_log}"

      if grep -Fxq "${norm_parent} -> ${norm_child}" "${pairs_log}"; then
        TF_STATIC_MATCH_ATTEMPT="${attempt}"
        return 0
      fi
    fi

    sleep 1
  done
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
    ros2 topic list >"${ARTIFACT_DIR}/04_realsense_topics_full.log" 2>"${ARTIFACT_DIR}/04_realsense_topics_full.err.log"
    local list_rc=$?
    set -e

    if [[ "${list_rc}" -eq 0 ]] \
      && grep -Fxq "/camera/realsense2_camera/color/image_raw" "${ARTIFACT_DIR}/04_realsense_topics_full.log" \
      && grep -Fxq "/camera/realsense2_camera/aligned_depth_to_color/image_raw" "${ARTIFACT_DIR}/04_realsense_topics_full.log" \
      && grep -Fxq "/camera/realsense2_camera/color/camera_info" "${ARTIFACT_DIR}/04_realsense_topics_full.log"; then
      set +e
      timeout 6s ros2 topic echo --once /camera/realsense2_camera/color/camera_info \
        >"${ARTIFACT_DIR}/04_realsense_camera_info_probe.out.log" \
        2>"${ARTIFACT_DIR}/04_realsense_camera_info_probe.err.log"
      local echo_rc=$?
      set -e
      if [[ "${echo_rc}" -eq 0 ]]; then
        return 0
      fi
    fi

    sleep 1
  done
}

try_echo_pc() {
  local topic="$1"
  local qos="$2"
  local out_log="$3"
  local err_log="$4"

  if [[ -n "${qos}" ]]; then
    timeout 8s ros2 topic echo --once "${topic}" --qos-reliability "${qos}" >"${out_log}" 2>"${err_log}"
  else
    timeout 8s ros2 topic echo --once "${topic}" >"${out_log}" 2>"${err_log}"
  fi
}

pick_lidar_topic() {
  local candidates=()
  if [[ -n "${PC_TOPIC_REQUESTED}" ]]; then
    candidates=("${PC_TOPIC_REQUESTED}")
  else
    candidates=("/utlidar/cloud" "/utlidar/cloud_base")
  fi

  ros2 topic list >"${ARTIFACT_DIR}/06_topics_all.out.log" 2>"${ARTIFACT_DIR}/06_topics_all.err.log" || true

  for candidate in "${candidates[@]}"; do
    if ! grep -Fxq "${candidate}" "${ARTIFACT_DIR}/06_topics_all.out.log"; then
      continue
    fi

    ros2 topic info -v "${candidate}" >"${ARTIFACT_DIR}/06_lidar_topic_info.log" 2>"${ARTIFACT_DIR}/06_lidar_topic_info.err.log" || true

    for qos in reliable best_effort ""; do
      set +e
      try_echo_pc "${candidate}" "${qos}" \
        "${ARTIFACT_DIR}/06_lidar_sample_${candidate//\//_}_${qos:-plain}.out.log" \
        "${ARTIFACT_DIR}/06_lidar_sample_${candidate//\//_}_${qos:-plain}.err.log"
      local rc=$?
      set -e
      if [[ "${rc}" -eq 0 ]]; then
        LIDAR_PC_TOPIC_USED="${candidate}"
        LIDAR_PC_QOS_USED="${qos:-plain}"
        return 0
      fi
    done
  done

  return 1
}

wait_scan_ready() {
  local timeout_sec="$1"
  local start_ts="$(date +%s)"

  while true; do
    local elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      return 1
    fi

    set +e
    timeout 6s ros2 topic echo --once "${SCAN_TOPIC}" --qos-reliability best_effort \
      >"${ARTIFACT_DIR}/08_scan_probe.out.log" \
      2>"${ARTIFACT_DIR}/08_scan_probe.err.log"
    local rc=$?
    set -e

    if [[ "${rc}" -eq 0 ]]; then
      return 0
    fi

    set +e
    timeout 6s ros2 topic echo --once "${SCAN_TOPIC}" \
      >"${ARTIFACT_DIR}/08_scan_probe_plain.out.log" \
      2>"${ARTIFACT_DIR}/08_scan_probe_plain.err.log"
    rc=$?
    set -e

    if [[ "${rc}" -eq 0 ]]; then
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

    set +e
    ros2 topic type /map >"${ARTIFACT_DIR}/10_map_topic_type.out.log" 2>"${ARTIFACT_DIR}/10_map_topic_type.err.log"
    local type_rc=$?
    set -e

    if [[ "${type_rc}" -eq 0 ]] && grep -q . "${ARTIFACT_DIR}/10_map_topic_type.out.log"; then
      set +e
      timeout 10s ros2 topic echo --once /map \
        >"${ARTIFACT_DIR}/10_map_probe.out.log" \
        2>"${ARTIFACT_DIR}/10_map_probe.err.log"
      local echo_rc=$?
      set -e
      if [[ "${echo_rc}" -eq 0 ]]; then
        return 0
      fi
    fi

    sleep 1
  done
}

check_tf_chain_best_effort() {
  local source_frame="$1"
  local target_frame="$2"
  local out_log="$3"
  local err_log="$4"

  set +e
  timeout 8s ros2 run tf2_ros tf2_echo "${source_frame}" "${target_frame}" >"${out_log}" 2>"${err_log}"
  local rc=$?
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
      >"${ARTIFACT_DIR}/08_scan_fresh_probe.out.log" \
      2>"${ARTIFACT_DIR}/08_scan_fresh_probe.err.log"
    local rc=$?
    set -e

    if [[ "${rc}" -eq 0 ]]; then
      return 0
    fi

    set +e
    timeout 6s ros2 topic echo --once "${SCAN_FRESH_TOPIC}" \
      >"${ARTIFACT_DIR}/08_scan_fresh_probe_plain.out.log" \
      2>"${ARTIFACT_DIR}/08_scan_fresh_probe_plain.err.log"
    rc=$?
    set -e

    if [[ "${rc}" -eq 0 ]]; then
      return 0
    fi

    sleep 1
  done
}

source_env

if [[ ! -f "${DB_PATH}" ]]; then
  step_log "FAIL: DB path not found inside container: ${DB_PATH}"
  exit 1
fi

if [[ ! -f "${SCAN_RESTAMP_HELPER}" ]]; then
  step_log "FAIL: scan restamp helper not found: ${SCAN_RESTAMP_HELPER}"
  exit 1
fi

if is_zero_triplet "${LIDAR_XYZ}" && is_zero_triplet "${LIDAR_RPY}"; then
  if [[ "${ALLOW_UNCALIBRATED_LIDAR}" -eq 1 ]]; then
    step_log "WARN: running with uncalibrated LiDAR extrinsics due to explicit override."
  else
    step_log "FAIL: lidar_xyz and lidar_rpy are both '0 0 0' (uncalibrated). Use calibrated values or --allow-uncalibrated-lidar."
    exit 1
  fi
fi

if is_zero_triplet "${CAMERA_XYZ}" && is_zero_triplet "${CAMERA_RPY}"; then
  step_log "WARN: camera_xyz and camera_rpy are both '0 0 0' (uncalibrated camera mount TF)."
fi

step_log "Starting board_description launch."
BOARD_PID="$(start_bg \
  "ros2 launch launch/board_description.launch.py lidar_frame:=${LIDAR_FRAME} lidar_xyz:='${LIDAR_XYZ}' lidar_rpy:='${LIDAR_RPY}' lidar_tf_required:=true camera_tf_required:=true camera_frame:=${CAMERA_FRAME} camera_xyz:='${CAMERA_XYZ}' camera_rpy:='${CAMERA_RPY}'" \
  "${ARTIFACT_DIR}/01_board_description.out.log" \
  "${ARTIFACT_DIR}/01_board_description.err.log")"

sleep 2
if ! kill -0 "${BOARD_PID}" 2>/dev/null; then
  step_log "FAIL: board_description exited early."
  tail -n 80 "${ARTIFACT_DIR}/01_board_description.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null
  exit 1
fi

if wait_tf_static_pair "base_link" "${LIDAR_FRAME}" 25; then
  step_log "PASS TF static pair: base_link->${LIDAR_FRAME} (attempt ${TF_STATIC_MATCH_ATTEMPT})"
else
  step_log "FAIL: TF static pair base_link->${LIDAR_FRAME} not observed."
  if [[ -f "${ARTIFACT_DIR}/02_tf_static_pairs.log" ]]; then
    step_log "Collected /tf_static pairs (latest):"
    tail -n 80 "${ARTIFACT_DIR}/02_tf_static_pairs.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  fi
  tail -n 60 "${ARTIFACT_DIR}/01_board_description.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  exit 1
fi

if wait_tf_static_pair "base_link" "${CAMERA_FRAME}" 25; then
  step_log "PASS TF static pair: base_link->${CAMERA_FRAME} (attempt ${TF_STATIC_MATCH_ATTEMPT})"
else
  step_log "FAIL: TF static pair base_link->${CAMERA_FRAME} not observed."
  if [[ -f "${ARTIFACT_DIR}/02_tf_static_pairs.log" ]]; then
    step_log "Collected /tf_static pairs (latest):"
    tail -n 80 "${ARTIFACT_DIR}/02_tf_static_pairs.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  fi
  tail -n 60 "${ARTIFACT_DIR}/01_board_description.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  exit 1
fi

step_log "Starting realsense launch."
REALSENSE_PID="$(start_bg \
  "ros2 launch launch/realsense_board.launch.py" \
  "${ARTIFACT_DIR}/03_realsense.out.log" \
  "${ARTIFACT_DIR}/03_realsense.err.log")"

if wait_realsense_ready 60; then
  step_log "PASS RealSense topics and camera_info probe."
else
  step_log "FAIL: RealSense topics did not become ready within 60s."
  ros2 node list >"${ARTIFACT_DIR}/04_realsense_nodes_full.log" 2>"${ARTIFACT_DIR}/04_realsense_nodes_full.err.log" || true
  grep -E "realsense" "${ARTIFACT_DIR}/04_realsense_nodes_full.log" >"${ARTIFACT_DIR}/04_realsense_nodes_filtered.log" || true
  ros2 topic list >"${ARTIFACT_DIR}/04_realsense_topics_full.log" 2>"${ARTIFACT_DIR}/04_realsense_topics_full.err.log" || true
  grep -E "realsense|image_raw|camera_info" "${ARTIFACT_DIR}/04_realsense_topics_full.log" >"${ARTIFACT_DIR}/04_realsense_topics_filtered.log" || true
  cat "${ARTIFACT_DIR}/04_realsense_nodes_filtered.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  cat "${ARTIFACT_DIR}/04_realsense_topics_filtered.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  exit 1
fi

if ! pick_lidar_topic; then
  step_log "FAIL: LiDAR mandatory but no readable PointCloud2 topic found (/utlidar/cloud or /utlidar/cloud_base)."
  exit 1
fi

step_log "PASS LiDAR sample read: topic=${LIDAR_PC_TOPIC_USED} qos=${LIDAR_PC_QOS_USED}"

step_log "Starting pointcloud_to_laserscan (${LIDAR_PC_TOPIC_USED} -> ${SCAN_TOPIC})."
PC2LS_PID="$(start_bg \
  "ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node --ros-args -p target_frame:=base_link -p transform_tolerance:=0.05 -p min_height:=-0.30 -p max_height:=0.50 -p angle_min:=-3.14159 -p angle_max:=3.14159 -p angle_increment:=0.0087 -p scan_time:=0.1 -p range_min:=0.10 -p range_max:=30.0 -p use_inf:=true -p inf_epsilon:=1.0 -r cloud_in:=${LIDAR_PC_TOPIC_USED} -r scan:=${SCAN_TOPIC}" \
  "${ARTIFACT_DIR}/07_pc2ls.out.log" \
  "${ARTIFACT_DIR}/07_pc2ls.err.log")"

if wait_scan_ready 20; then
  step_log "PASS scan check: ${SCAN_TOPIC} is publishing."
else
  step_log "FAIL: ${SCAN_TOPIC} not publishing after pointcloud_to_laserscan start."
  tail -n 80 "${ARTIFACT_DIR}/07_pc2ls.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  ros2 topic list >"${ARTIFACT_DIR}/08_topics_after_scan_fail.log" 2>/dev/null || true
  grep -E "scan" "${ARTIFACT_DIR}/08_topics_after_scan_fail.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  exit 1
fi

step_log "Starting scan_restamp (${SCAN_TOPIC} -> ${SCAN_FRESH_TOPIC})."
SCAN_RESTAMP_PID="$(start_bg \
  "python3 ${SCAN_RESTAMP_HELPER} ${SCAN_TOPIC} ${SCAN_FRESH_TOPIC}" \
  "${ARTIFACT_DIR}/08_scan_restamp.out.log" \
  "${ARTIFACT_DIR}/08_scan_restamp.err.log")"

if wait_scan_fresh_ready 20; then
  step_log "PASS scan restamp check: ${SCAN_FRESH_TOPIC} is publishing."
else
  step_log "FAIL: ${SCAN_FRESH_TOPIC} not publishing after scan_restamp start."
  tail -n 80 "${ARTIFACT_DIR}/08_scan_restamp.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  tail -n 80 "${ARTIFACT_DIR}/08_scan_restamp.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  exit 1
fi

step_log "Starting RTAB-Map localization."
LOCALIZATION_PID="$(start_bg \
  "ros2 launch launch/rtabmap_localization.launch.py database_path:='${DB_PATH}' rgb_topic:=/camera/realsense2_camera/color/image_raw depth_topic:=/camera/realsense2_camera/aligned_depth_to_color/image_raw camera_info_topic:=/camera/realsense2_camera/color/camera_info scan_topic:=${SCAN_FRESH_TOPIC} base_frame:=base_link odom_frame:=odom map_frame:=map" \
  "${ARTIFACT_DIR}/09_localization.out.log" \
  "${ARTIFACT_DIR}/09_localization.err.log")"

if wait_map_ready 45; then
  step_log "PASS localization up: /map type resolved and one message received."
else
  step_log "FAIL: localization started but /map not received."
  timeout 6s ros2 topic hz /rgbd_image >"${ARTIFACT_DIR}/10_rgbd_hz.out.log" 2>"${ARTIFACT_DIR}/10_rgbd_hz.err.log" || true
  timeout 6s ros2 topic hz "${SCAN_FRESH_TOPIC}" >"${ARTIFACT_DIR}/10_scan_fresh_hz.out.log" 2>"${ARTIFACT_DIR}/10_scan_fresh_hz.err.log" || true
  grep -E "rgbd_sync.*subscrib|rtabmap.*subscrib|Subscribed to|subscribe" "${ARTIFACT_DIR}/09_localization.out.log" >"${ARTIFACT_DIR}/10_localization_subscriptions.log" || true
  ros2 topic list >"${ARTIFACT_DIR}/10_topic_list_post_localization.log" 2>/dev/null || true
  grep -E '^/map$|^/rgbd_image$|^/scan$|^/scan_fresh$|rtabmap' "${ARTIFACT_DIR}/10_topic_list_post_localization.log" >"${ARTIFACT_DIR}/10_topic_list_filtered.log" || true
  cat "${ARTIFACT_DIR}/10_localization_subscriptions.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  cat "${ARTIFACT_DIR}/10_rgbd_hz.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  cat "${ARTIFACT_DIR}/10_scan_fresh_hz.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  cat "${ARTIFACT_DIR}/10_topic_list_filtered.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  if check_tf_chain_best_effort "base_link" "camera_color_optical_frame" "${ARTIFACT_DIR}/10_tf_echo_base_to_camera_optical.out.log" "${ARTIFACT_DIR}/10_tf_echo_base_to_camera_optical.err.log"; then
    step_log "INFO: best-effort TF chain check PASS (base_link -> camera_color_optical_frame)."
  else
    step_log "INFO: best-effort TF chain check FAIL (base_link -> camera_color_optical_frame)."
    tail -n 40 "${ARTIFACT_DIR}/10_tf_echo_base_to_camera_optical.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  fi
  tail -n 80 "${ARTIFACT_DIR}/08_scan_restamp.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  tail -n 80 "${ARTIFACT_DIR}/08_scan_restamp.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  tail -n 80 "${ARTIFACT_DIR}/09_localization.out.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  tail -n 80 "${ARTIFACT_DIR}/09_localization.err.log" | tee -a "${ARTIFACT_DIR}/summary.log" >/dev/null || true
  exit 1
fi

{
  echo "db_path=${DB_PATH}"
  echo "lidar_frame=${LIDAR_FRAME}"
  echo "lidar_xyz=${LIDAR_XYZ}"
  echo "lidar_rpy=${LIDAR_RPY}"
  echo "lidar_pc_topic_used=${LIDAR_PC_TOPIC_USED}"
  echo "lidar_pc_qos_used=${LIDAR_PC_QOS_USED}"
  echo "scan_topic=${SCAN_TOPIC}"
  echo "scan_fresh_topic=${SCAN_FRESH_TOPIC}"
  echo "camera_frame=${CAMERA_FRAME}"
  echo "camera_xyz=${CAMERA_XYZ}"
  echo "camera_rpy=${CAMERA_RPY}"
} >"${ARTIFACT_DIR}/manifest.txt"

step_log "Localization visualization stack is running. Press Ctrl+C to stop all processes."
while true; do
  sleep 1
done
INNER_EOF

chmod +x "${INNER_SCRIPT_HOST}"

set +e
docker exec "${CONTAINER_NAME}" bash -lc \
  "/workspace/repo/artifacts/rtabmap_localization/${TIMESTAMP}/localization_inner.sh /workspace/repo/artifacts/rtabmap_localization/${TIMESTAMP} '${container_db_path}' '${PC_TOPIC}' '${SCAN_TOPIC}' '${LIDAR_FRAME}' '${LIDAR_XYZ}' '${LIDAR_RPY}' '${ALLOW_UNCALIBRATED_LIDAR}' '${CAMERA_FRAME}' '${CAMERA_XYZ}' '${CAMERA_RPY}'" \
  > >(tee "${RUN_DIR}/99_inner_wrapper.out.log") \
  2> >(tee "${RUN_DIR}/99_inner_wrapper.err.log" >&2)
rc=$?
set -e

if [[ "${rc}" -ne 0 ]]; then
  log "FAIL: RTAB-Map localization visualize failed (rc=${rc})."
  log "Inspect ${RUN_DIR}/summary.log and component logs under ${RUN_DIR}."
  exit "${rc}"
fi

log "Stopped localization visualization stack."
