#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOPICS_FILE="${TOPICS_FILE:-${ROOT_DIR}/config/runtime_topics.yaml}"
SUMMARY_PREFIX="[run_localization_board]"
D410_FALLBACK_MODE=0

usage() {
  cat <<'USAGE'
Usage:
  scripts/rtabmap/run_localization_board.sh [options]

Options:
  --d410-fallback-mode   NOTBETRIEBSMODUS: use infra1+depth topics instead of color+aligned_depth_to_color
  -h, --help             Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --d410-fallback-mode)
      D410_FALLBACK_MODE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "${SUMMARY_PREFIX} ERROR: unknown argument '$1'" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v ros2 >/dev/null 2>&1; then
  echo "[run_localization_board] ERROR: ros2 CLI not found in PATH." >&2
  exit 1
fi

if [[ ! -f "${TOPICS_FILE}" ]]; then
  echo "${SUMMARY_PREFIX} ERROR: runtime topics file not found: ${TOPICS_FILE}" >&2
  exit 1
fi

latest_map_db() {
  local maps_root="${ROOT_DIR}/artifacts/maps"
  local latest_link="${maps_root}/latest"
  local resolved=""
  if [[ -L "${latest_link}" ]]; then
    resolved="$(cd "$(dirname "${latest_link}")" && readlink "${latest_link}")"
    if [[ -n "${resolved}" && "${resolved}" = /* && -f "${resolved}/rtabmap.db" ]]; then
      printf '%s\n' "${resolved}/rtabmap.db"
      return 0
    fi
    if [[ -n "${resolved}" && -f "${maps_root}/${resolved}/rtabmap.db" ]]; then
      printf '%s\n' "${maps_root}/${resolved}/rtabmap.db"
      return 0
    fi
  fi

  find "${maps_root}" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' 2>/dev/null \
    | sort -nr \
    | awk '{print $2}' \
    | while IFS= read -r run_dir; do
        [[ -f "${run_dir}/rtabmap.db" ]] || continue
        printf '%s\n' "${run_dir}/rtabmap.db"
        break
      done
}

latest_manual_extrinsics() {
  local manual_root="${ROOT_DIR}/artifacts/manual_calibration"
  local latest_link="${manual_root}/latest"
  local resolved=""
  if [[ -L "${latest_link}" ]]; then
    resolved="$(cd "$(dirname "${latest_link}")" && readlink "${latest_link}")"
    if [[ -n "${resolved}" && "${resolved}" = /* && -f "${resolved}/manual_sensor_extrinsics.env" ]]; then
      printf '%s\n' "${resolved}/manual_sensor_extrinsics.env"
      return 0
    fi
    if [[ -n "${resolved}" && -f "${manual_root}/${resolved}/manual_sensor_extrinsics.env" ]]; then
      printf '%s\n' "${manual_root}/${resolved}/manual_sensor_extrinsics.env"
      return 0
    fi
  fi

  find "${manual_root}" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' 2>/dev/null \
    | sort -nr \
    | awk '{print $2}' \
    | while IFS= read -r run_dir; do
        [[ -f "${run_dir}/manual_sensor_extrinsics.env" ]] || continue
        printf '%s\n' "${run_dir}/manual_sensor_extrinsics.env"
        break
      done
}

read_yaml_value() {
  local key="$1"
  awk -F': *' -v key="${key}" '$1 ~ "^[[:space:]]*"key"$" {print $2}' "${TOPICS_FILE}" \
    | tr -d '"' \
    | tail -n 1
}

RGB_TOPIC="${RGB_TOPIC:-$(read_yaml_value rgb_topic)}"
DEPTH_TOPIC="${DEPTH_TOPIC:-$(read_yaml_value depth_topic)}"
CAMERA_INFO_TOPIC="${CAMERA_INFO_TOPIC:-$(read_yaml_value camera_info_topic)}"
BASE_FRAME="${BASE_FRAME:-$(read_yaml_value base_frame)}"
ODOM_FRAME="${ODOM_FRAME:-$(read_yaml_value odom_frame)}"
MAP_FRAME="${MAP_FRAME:-$(read_yaml_value map_frame)}"
DATABASE_PATH="${DATABASE_PATH:-$(read_yaml_value database_path)}"

if [[ "${D410_FALLBACK_MODE}" -eq 1 ]]; then
  RGB_TOPIC="/camera/realsense2_camera/infra1/image_rect_raw"
  DEPTH_TOPIC="/camera/realsense2_camera/depth/image_rect_raw"
  CAMERA_INFO_TOPIC="/camera/realsense2_camera/infra1/camera_info"
fi

if [[ -z "${DATABASE_PATH}" || "${DATABASE_PATH}" == "<"*">" ]]; then
  DATABASE_PATH="$(latest_map_db || true)"
fi

for value_name in RGB_TOPIC DEPTH_TOPIC CAMERA_INFO_TOPIC DATABASE_PATH; do
  value="${!value_name:-}"
  if [[ -z "${value}" || "${value}" == "<"*">" ]]; then
    echo "${SUMMARY_PREFIX} ERROR: ${value_name} is unset/placeholder. Update ${TOPICS_FILE} or provide a current artifacts/maps/*/rtabmap.db." >&2
    exit 2
  fi
done

echo "${SUMMARY_PREFIX} Launching RTAB-Map localization with:"
echo "  rgb_topic=${RGB_TOPIC}"
echo "  depth_topic=${DEPTH_TOPIC}"
echo "  camera_info_topic=${CAMERA_INFO_TOPIC}"
echo "  database_path=${DATABASE_PATH}"
if [[ "${D410_FALLBACK_MODE}" -eq 1 ]]; then
  echo "${SUMMARY_PREFIX} RealSense NOTBETRIEBSMODUS active (infra1+depth fallback)."
fi
if latest_manual_env="$(latest_manual_extrinsics || true)"; [[ -n "${latest_manual_env}" ]]; then
  echo "${SUMMARY_PREFIX} Preferred session extrinsics for the surrounding board_description path: ${latest_manual_env}"
else
  echo "${SUMMARY_PREFIX} No manual session extrinsics found; higher-level runners may fall back to older calibration sources."
fi
echo "${SUMMARY_PREFIX} This low-level helper launches RTAB-Map only; for full board_description + current session extrinsics use scripts/rtabmap/run_r3_localization_visualize.sh"

ros2 launch launch/rtabmap_localization.launch.py \
  rgb_topic:="${RGB_TOPIC}" \
  depth_topic:="${DEPTH_TOPIC}" \
  camera_info_topic:="${CAMERA_INFO_TOPIC}" \
  base_frame:="${BASE_FRAME:-base_link}" \
  odom_frame:="${ODOM_FRAME:-odom}" \
  map_frame:="${MAP_FRAME:-map}" \
  database_path:="${DATABASE_PATH}"
