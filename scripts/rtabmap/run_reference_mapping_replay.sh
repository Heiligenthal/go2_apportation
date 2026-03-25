#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ARTIFACT_ROOT="${ROOT_DIR}/artifacts"
CALIBRATION_ROOT="${ARTIFACT_ROOT}/calibration/camera_mount"
REFERENCE_ROOT="${ARTIFACT_ROOT}/reference_mapping"
MAPS_ROOT="${ARTIFACT_ROOT}/maps"

COLOR_TOPIC="/camera/realsense2_camera/color/image_raw"
DEPTH_TOPIC="/camera/realsense2_camera/aligned_depth_to_color/image_raw"
CAMERA_INFO_TOPIC="/camera/realsense2_camera/color/camera_info"
ODOM_TOPIC="/utlidar/robot_odom"
SCAN_TOPIC="/scan"

REPLAY_RUN_DIR=""
REPLAY_MAP_DIR=""
ODOM_TF_PID=""
CAMERA_TF_PID=""
OPTICAL_TF_PID=""
MAPPING_PID=""

usage() {
  cat <<'USAGE'
Usage:
  scripts/rtabmap/run_reference_mapping_replay.sh [options]

Options:
  --bag <path>                 Explicit rosbag2 directory (default: SOURCE_BAG from latest calibration)
  --extrinsics-env <path>      Explicit best_extrinsics.env (default: latest calibration run)
  --output-tag <tag>           Use a fixed output tag instead of a timestamp
  --with-scan                  Replay /scan too and enable subscribe_scan
  -h, --help                   Show this help
USAGE
}

log() {
  printf '[run_reference_mapping_replay] %s\n' "$*"
}

die() {
  printf '[run_reference_mapping_replay] ERROR: %s\n' "$*" >&2
  exit 1
}

source_bash_file() {
  local file_path rc
  file_path="$1"

  set +e
  # shellcheck disable=SC1090
  source "$file_path"
  rc=$?
  set -e

  return "$rc"
}

source_ros_env() {
  local ros_setup ws_container_setup ws_setup ws_local_setup

  set +u
  ros_setup="/opt/ros/humble/setup.bash"
  [[ -f "$ros_setup" ]] || die "ROS 2 Humble setup not found at $ros_setup. Run this script inside the intended Board-Runtime Docker container."
  source_bash_file "$ros_setup" || die "Failed to source ROS 2 Humble setup: $ros_setup"
  log "Sourced $ros_setup"

  ws_container_setup="${ROOT_DIR}/install_container/setup.bash"
  ws_setup="${ROOT_DIR}/install/setup.bash"
  ws_local_setup="${ROOT_DIR}/install/local_setup.bash"

  if [[ -f "$ws_container_setup" ]] && source_bash_file "$ws_container_setup"; then
    log "Sourced $ws_container_setup"
  elif [[ -f "$ws_setup" ]] && source_bash_file "$ws_setup"; then
    log "Sourced $ws_setup"
  elif [[ -f "$ws_local_setup" ]] && source_bash_file "$ws_local_setup"; then
    log "Sourced $ws_local_setup as local workspace overlay fallback"
  else
    die "No workspace overlay could be sourced. Tried: $ws_container_setup, $ws_setup, $ws_local_setup"
  fi
  set -u
}

ensure_tools() {
  command -v ros2 >/dev/null 2>&1 || die "ros2 not found in PATH after sourcing environment."
  command -v python3 >/dev/null 2>&1 || die "python3 not found in PATH."
  command -v rtabmap-reprocess >/dev/null 2>&1 || die "rtabmap-reprocess not found in PATH."
  command -v rtabmap-info >/dev/null 2>&1 || die "rtabmap-info not found in PATH."
}

latest_valid_bag() {
  find "${ARTIFACT_ROOT}/bags" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' 2>/dev/null \
    | sort -nr \
    | awk '{print $2}' \
    | while IFS= read -r bag; do
        [[ -f "$bag/metadata.yaml" ]] || continue
        printf '%s\n' "$bag"
        break
      done
}

latest_calibration_dir() {
  local latest_link resolved
  latest_link="${CALIBRATION_ROOT}/latest"
  if [[ -L "${latest_link}" ]]; then
    resolved="$(cd "$(dirname "${latest_link}")" && readlink "${latest_link}")"
    if [[ -n "${resolved}" && -d "${CALIBRATION_ROOT}/${resolved}" ]]; then
      printf '%s\n' "${CALIBRATION_ROOT}/${resolved}"
      return 0
    fi
  fi

  find "${CALIBRATION_ROOT}" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' 2>/dev/null \
    | sort -nr \
    | awk '{print $2}' \
    | while IFS= read -r run_dir; do
        [[ -f "${run_dir}/best_extrinsics.env" ]] || continue
        printf '%s\n' "${run_dir}"
        break
      done
}

resolve_path() {
  local path_value="$1"
  if [[ "${path_value}" = /* ]]; then
    printf '%s\n' "${path_value}"
  else
    printf '%s\n' "${ROOT_DIR}/${path_value}"
  fi
}

deg_to_rad() {
  python3 - "$1" <<'PY'
import math
import sys
print(math.radians(float(sys.argv[1])))
PY
}

wait_for_nodes_ready() {
  local timeout_seconds="$1"
  shift || true
  local deadline node node_list
  deadline=$((SECONDS + timeout_seconds))
  while ((SECONDS < deadline)); do
    node_list="$(ros2 node list 2>/dev/null || true)"
    if [[ -n "${node_list}" ]]; then
      local all_found=1
      for node in "$@"; do
        if ! grep -Fxq "${node}" <<<"${node_list}"; then
          all_found=0
          break
        fi
      done
      if [[ "${all_found}" -eq 1 ]]; then
        return 0
      fi
    fi
    sleep 1
  done
  return 1
}

check_replay_clock_mismatch() {
  local log_path
  for log_path in "$@"; do
    [[ -f "${log_path}" ]] || continue
    if grep -Eq 'Lookup would require extrapolation into the past|TF_OLD_DATA' "${log_path}"; then
      printf 'Replay TF/clock mismatch\n' >"${REPLAY_RUN_DIR}/db_sanity.log"
      printf 'log_path=%s\n' "${log_path}" >>"${REPLAY_RUN_DIR}/db_sanity.log"
      printf 'db_path=%s\n' "${REPLAY_MAP_DIR}/rtabmap.db" >>"${REPLAY_RUN_DIR}/db_sanity.log"
      printf '[run_reference_mapping_replay] ERROR: Replay TF/clock mismatch. See %s and %s\n' \
        "${log_path}" "${REPLAY_RUN_DIR}/db_sanity.log" >&2
      return 1
    fi
  done
  return 0
}

stop_pid() {
  local pid="$1"
  local name="$2"
  [[ -n "${pid}" ]] || return 0
  if ! kill -0 "${pid}" 2>/dev/null; then
    return 0
  fi
  kill -INT "${pid}" >/dev/null 2>&1 || true
  for _ in $(seq 1 8); do
    if ! kill -0 "${pid}" 2>/dev/null; then
      wait "${pid}" >/dev/null 2>&1 || true
      log "Stopped ${name} (pid=${pid})"
      return 0
    fi
    sleep 1
  done
  kill -TERM "${pid}" >/dev/null 2>&1 || true
  wait "${pid}" >/dev/null 2>&1 || true
  log "Stopped ${name} (pid=${pid})"
}

cleanup() {
  set +e
  stop_pid "${MAPPING_PID}" "rtabmap_mapping"
  stop_pid "${OPTICAL_TF_PID}" "camera_optical_static_tf"
  stop_pid "${CAMERA_TF_PID}" "camera_mount_static_tf"
  stop_pid "${ODOM_TF_PID}" "odom_to_tf_broadcaster"
}

update_latest_symlink() {
  mkdir -p "${REFERENCE_ROOT}"
  if [[ -L "${REFERENCE_ROOT}/latest" || -e "${REFERENCE_ROOT}/latest" ]]; then
    rm -rf "${REFERENCE_ROOT}/latest"
  fi
  ln -s "${REPLAY_RUN_DIR}" "${REFERENCE_ROOT}/latest"
}

main() {
  local bag_path=""
  local extrinsics_env=""
  local output_tag=""
  local with_scan=0
  local latest_run bootstrap_summary best_yaml

  while (($#)); do
    case "$1" in
      --bag)
        shift || die "Missing value after --bag"
        bag_path="$1"
        ;;
      --extrinsics-env)
        shift || die "Missing value after --extrinsics-env"
        extrinsics_env="$1"
        ;;
      --output-tag)
        shift || die "Missing value after --output-tag"
        output_tag="$1"
        ;;
      --with-scan)
        with_scan=1
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "Unknown argument '$1'"
        ;;
    esac
    shift || true
  done

  source_ros_env
  ensure_tools
  trap cleanup EXIT INT TERM

  latest_run="$(latest_calibration_dir || true)"
  [[ -n "${latest_run}" ]] || die "No calibration run with best_extrinsics.env found under ${CALIBRATION_ROOT}"
  best_yaml="${latest_run}/best_extrinsics.yaml"
  bootstrap_summary="${latest_run}/bootstrap_summary.yaml"

  if [[ -z "${extrinsics_env}" ]]; then
    extrinsics_env="${latest_run}/best_extrinsics.env"
  else
    extrinsics_env="$(resolve_path "${extrinsics_env}")"
  fi
  [[ -f "${extrinsics_env}" ]] || die "Extrinsics env file not found: ${extrinsics_env}"

  set -a
  # shellcheck disable=SC1090
  source "${extrinsics_env}"
  set +a

  [[ -n "${X:-}" && -n "${Y:-}" && -n "${Z:-}" ]] || die "Extrinsics env is missing X/Y/Z: ${extrinsics_env}"
  [[ -n "${ROLL_DEG:-}" && -n "${PITCH_DEG:-}" && -n "${YAW_DEG:-}" ]] || die "Extrinsics env is missing roll/pitch/yaw: ${extrinsics_env}"
  [[ -n "${CAMERA_INFO_FRAME:-}" ]] || die "Extrinsics env is missing CAMERA_INFO_FRAME: ${extrinsics_env}"
  [[ -n "${OPTICAL_TO_CAMERA_LINK_XYZ:-}" ]] || die "Extrinsics env is missing OPTICAL_TO_CAMERA_LINK_XYZ: ${extrinsics_env}"
  [[ -n "${OPTICAL_TO_CAMERA_LINK_RPY_DEG:-}" ]] || die "Extrinsics env is missing OPTICAL_TO_CAMERA_LINK_RPY_DEG: ${extrinsics_env}"

  if [[ -z "${bag_path}" ]]; then
    bag_path="${SOURCE_BAG:-}"
  else
    bag_path="$(resolve_path "${bag_path}")"
  fi
  if [[ -z "${bag_path}" ]]; then
    bag_path="$(latest_valid_bag || true)"
  fi
  [[ -n "${bag_path}" ]] || die "No input bag resolved."
  [[ -d "${bag_path}" && -f "${bag_path}/metadata.yaml" ]] || die "Bag path is not a valid rosbag2 directory with metadata.yaml: ${bag_path}"

  if [[ -z "${output_tag}" ]]; then
    output_tag="$(date +%Y%m%d_%H%M%S)"
  fi

  REPLAY_RUN_DIR="${REFERENCE_ROOT}/${output_tag}"
  REPLAY_MAP_DIR="${MAPS_ROOT}/${output_tag}"
  [[ ! -e "${REPLAY_RUN_DIR}" ]] || die "Replay run dir already exists: ${REPLAY_RUN_DIR}"
  [[ ! -e "${REPLAY_MAP_DIR}" ]] || die "Replay map dir already exists: ${REPLAY_MAP_DIR}"
  mkdir -p "${REPLAY_RUN_DIR}" "${REPLAY_MAP_DIR}"

  cp -a "${extrinsics_env}" "${REPLAY_RUN_DIR}/best_extrinsics.env"
  [[ -f "${best_yaml}" ]] && cp -a "${best_yaml}" "${REPLAY_RUN_DIR}/best_extrinsics.yaml"
  [[ -f "${bootstrap_summary}" ]] && cp -a "${bootstrap_summary}" "${REPLAY_RUN_DIR}/bootstrap_summary.yaml"

  local roll_rad pitch_rad yaw_rad optical_roll_rad optical_pitch_rad optical_yaw_rad
  roll_rad="$(deg_to_rad "${ROLL_DEG}")"
  pitch_rad="$(deg_to_rad "${PITCH_DEG}")"
  yaw_rad="$(deg_to_rad "${YAW_DEG}")"

  read -r optical_x optical_y optical_z <<<"${OPTICAL_TO_CAMERA_LINK_XYZ}"
  read -r optical_roll_deg optical_pitch_deg optical_yaw_deg <<<"${OPTICAL_TO_CAMERA_LINK_RPY_DEG}"
  optical_roll_rad="$(deg_to_rad "${optical_roll_deg}")"
  optical_pitch_rad="$(deg_to_rad "${optical_pitch_deg}")"
  optical_yaw_rad="$(deg_to_rad "${optical_yaw_deg}")"

  log "Using calibration run: ${latest_run}"
  log "Using best extrinsics env: ${extrinsics_env}"
  log "Using bag: ${bag_path}"
  log "Output run dir: ${REPLAY_RUN_DIR}"
  log "Output map dir: ${REPLAY_MAP_DIR}"
  log "Replay subscribe_scan=${with_scan}"

  ros2 run go2_tf_tools odom_to_tf_broadcaster \
    --ros-args \
    -p "use_sim_time:=true" \
    -p "odom_topic:=${ODOM_TOPIC}" \
    -p "parent_frame:=odom" \
    -p "child_frame:=base_link" \
    -p "stamp_source:=now" \
    >"${REPLAY_RUN_DIR}/01_odom_tf.out.log" \
    2>"${REPLAY_RUN_DIR}/01_odom_tf.err.log" &
  ODOM_TF_PID="$!"

  ros2 run tf2_ros static_transform_publisher \
    "${X}" "${Y}" "${Z}" \
    "${roll_rad}" "${pitch_rad}" "${yaw_rad}" \
    base_link camera_link \
    --ros-args -p use_sim_time:=true \
    >"${REPLAY_RUN_DIR}/02_camera_mount_tf.out.log" \
    2>"${REPLAY_RUN_DIR}/02_camera_mount_tf.err.log" &
  CAMERA_TF_PID="$!"

  ros2 run tf2_ros static_transform_publisher \
    "${optical_x}" "${optical_y}" "${optical_z}" \
    "${optical_roll_rad}" "${optical_pitch_rad}" "${optical_yaw_rad}" \
    camera_link "${CAMERA_INFO_FRAME}" \
    --ros-args -p use_sim_time:=true \
    >"${REPLAY_RUN_DIR}/03_camera_optical_tf.out.log" \
    2>"${REPLAY_RUN_DIR}/03_camera_optical_tf.err.log" &
  OPTICAL_TF_PID="$!"

  ros2 launch launch/rtabmap_mapping.launch.py \
    use_sim_time:=true \
    "subscribe_scan:=$([[ "${with_scan}" -eq 1 ]] && echo true || echo false)" \
    "database_path:=${REPLAY_MAP_DIR}/rtabmap.db" \
    "rgb_topic:=${COLOR_TOPIC}" \
    "depth_topic:=${DEPTH_TOPIC}" \
    "camera_info_topic:=${CAMERA_INFO_TOPIC}" \
    "scan_topic:=${SCAN_TOPIC}" \
    base_frame:=base_link \
    odom_frame:=odom \
    map_frame:=map \
    >"${REPLAY_RUN_DIR}/04_mapping.out.log" \
    2>"${REPLAY_RUN_DIR}/04_mapping.err.log" &
  MAPPING_PID="$!"

  if ! wait_for_nodes_ready 20 "/rgbd_sync" "/rtabmap"; then
    die "Replay mapping nodes did not become ready before bag replay. DB target=${REPLAY_MAP_DIR}/rtabmap.db. Logs: ${REPLAY_RUN_DIR}/04_mapping.out.log ${REPLAY_RUN_DIR}/04_mapping.err.log"
  fi

  local -a play_topics=(
    "${COLOR_TOPIC}"
    "${DEPTH_TOPIC}"
    "${CAMERA_INFO_TOPIC}"
    "${ODOM_TOPIC}"
  )
  if [[ "${with_scan}" -eq 1 ]]; then
    play_topics+=("${SCAN_TOPIC}")
  fi

  ros2 bag play "${bag_path}" \
    --clock 50.0 \
    --topics "${play_topics[@]}" \
    >"${REPLAY_RUN_DIR}/05_bag_play.out.log" \
    2>"${REPLAY_RUN_DIR}/05_bag_play.err.log"

  sleep 3
  stop_pid "${MAPPING_PID}" "rtabmap_mapping"
  MAPPING_PID=""

  check_replay_clock_mismatch \
    "${REPLAY_RUN_DIR}/01_odom_tf.err.log" \
    "${REPLAY_RUN_DIR}/04_mapping.err.log" \
    "${REPLAY_RUN_DIR}/05_bag_play.err.log" || exit 1

  [[ -f "${REPLAY_MAP_DIR}/rtabmap.db" ]] || die "Replay mapping did not produce ${REPLAY_MAP_DIR}/rtabmap.db"
  python3 "${ROOT_DIR}/scripts/rtabmap/check_rtabmap_db_sanity.py" \
    --db "${REPLAY_MAP_DIR}/rtabmap.db" \
    --context "reference-map replay" \
    --artifact-dir "${REPLAY_RUN_DIR}" \
    --log-path "${REPLAY_RUN_DIR}/04_mapping.out.log" \
    --log-path "${REPLAY_RUN_DIR}/04_mapping.err.log" \
    --log-path "${REPLAY_RUN_DIR}/05_bag_play.out.log" \
    --log-path "${REPLAY_RUN_DIR}/05_bag_play.err.log" \
    >"${REPLAY_RUN_DIR}/db_sanity.log" \
    2>&1 || {
      cat "${REPLAY_RUN_DIR}/db_sanity.log" >&2
      die "Replay mapping produced a missing or semantically empty RTAB-Map DB. See ${REPLAY_RUN_DIR}/db_sanity.log"
    }

  rtabmap-reprocess -g2 "${REPLAY_MAP_DIR}/rtabmap.db" "${REPLAY_MAP_DIR}/_reprocess_export.db" \
    >"${REPLAY_RUN_DIR}/06_export.out.log" \
    2>"${REPLAY_RUN_DIR}/06_export.err.log"
  [[ -f "${REPLAY_MAP_DIR}/_reprocess_export_map.pgm" ]] || die "Expected exported map image was not generated."
  mv -f "${REPLAY_MAP_DIR}/_reprocess_export_map.pgm" "${REPLAY_MAP_DIR}/map.pgm"

  rtabmap-info --dump "${REPLAY_MAP_DIR}/_db_params.ini" "${REPLAY_MAP_DIR}/rtabmap.db" \
    >>"${REPLAY_RUN_DIR}/06_export.out.log" \
    2>>"${REPLAY_RUN_DIR}/06_export.err.log"
  resolution="$(awk -F= '$1=="Grid/CellSize" {print $2}' "${REPLAY_MAP_DIR}/_db_params.ini" | tail -n 1)"
  [[ -n "${resolution}" ]] || resolution="0.05"
  cat >"${REPLAY_MAP_DIR}/map.yaml" <<YAML
image: map.pgm
resolution: ${resolution}
origin: [0.0, 0.0, 0.0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.196
YAML
  rm -f "${REPLAY_MAP_DIR}/_reprocess_export.db" "${REPLAY_MAP_DIR}/_db_params.ini"

  python3 "${ROOT_DIR}/scripts/rtabmap/evaluate_map_artifacts.py" \
    --map-dir "${REPLAY_MAP_DIR}" \
    --run-dir "${REPLAY_RUN_DIR}" \
    >"${REPLAY_RUN_DIR}/evaluation.txt"

  cp -a "${extrinsics_env}" "${REPLAY_MAP_DIR}/best_extrinsics.env"
  [[ -f "${best_yaml}" ]] && cp -a "${best_yaml}" "${REPLAY_MAP_DIR}/best_extrinsics.yaml"
  [[ -f "${bootstrap_summary}" ]] && cp -a "${bootstrap_summary}" "${REPLAY_MAP_DIR}/bootstrap_summary.yaml"

  cat >"${REPLAY_MAP_DIR}/manifest.txt" <<EOF
source_bag=${bag_path}
calibration_run=${latest_run}
extrinsics_env=${extrinsics_env}
camera_info_frame=${CAMERA_INFO_FRAME}
camera_link_frame=${CAMERA_LINK_FRAME:-camera_link}
camera_xyz=${X} ${Y} ${Z}
camera_rpy=${ROLL_DEG} ${PITCH_DEG} ${YAW_DEG}
optical_to_camera_link_xyz=${OPTICAL_TO_CAMERA_LINK_XYZ}
optical_to_camera_link_rpy_deg=${OPTICAL_TO_CAMERA_LINK_RPY_DEG}
subscribe_scan=$([[ "${with_scan}" -eq 1 ]] && echo true || echo false)
EOF

  cat >"${REPLAY_RUN_DIR}/summary.txt" <<EOF
reference_map_dir=${REPLAY_MAP_DIR}
source_bag=${bag_path}
calibration_run=${latest_run}
extrinsics_env=${extrinsics_env}
subscribe_scan=$([[ "${with_scan}" -eq 1 ]] && echo true || echo false)
EOF

  update_latest_symlink
  log "Reference replay mapping completed."
  log "Map directory: ${REPLAY_MAP_DIR}"
  log "Run directory: ${REPLAY_RUN_DIR}"
  log "Evaluation: ${REPLAY_RUN_DIR}/evaluation.txt"
}

main "$@"
