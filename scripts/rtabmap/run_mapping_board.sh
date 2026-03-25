#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOPICS_FILE="${TOPICS_FILE:-${ROOT_DIR}/config/runtime_topics.yaml}"

if ! command -v ros2 >/dev/null 2>&1; then
  echo "[run_mapping_board] ERROR: ros2 CLI not found in PATH." >&2
  exit 1
fi

if [[ ! -f "${TOPICS_FILE}" ]]; then
  echo "[run_mapping_board] ERROR: runtime topics file not found: ${TOPICS_FILE}" >&2
  exit 1
fi

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
USE_SIM_TIME="${USE_SIM_TIME:-false}"

for value_name in RGB_TOPIC DEPTH_TOPIC CAMERA_INFO_TOPIC; do
  value="${!value_name:-}"
  if [[ -z "${value}" || "${value}" == "<"*">" ]]; then
    echo "[run_mapping_board] ERROR: ${value_name} is unset/placeholder. Update ${TOPICS_FILE}." >&2
    exit 2
  fi
done

echo "[run_mapping_board] Launching RTAB-Map mapping with:"
echo "  rgb_topic=${RGB_TOPIC}"
echo "  depth_topic=${DEPTH_TOPIC}"
echo "  camera_info_topic=${CAMERA_INFO_TOPIC}"
echo "  base_frame=${BASE_FRAME:-base_link} odom_frame=${ODOM_FRAME:-odom} map_frame=${MAP_FRAME:-map}"
if [[ -n "${DATABASE_PATH}" && "${DATABASE_PATH}" != "<"*">" ]]; then
  echo "  database_path=${DATABASE_PATH}"
fi
echo "  use_sim_time=${USE_SIM_TIME}"

launch_args=(
  "rgb_topic:=${RGB_TOPIC}"
  "depth_topic:=${DEPTH_TOPIC}"
  "camera_info_topic:=${CAMERA_INFO_TOPIC}"
  "base_frame:=${BASE_FRAME:-base_link}"
  "odom_frame:=${ODOM_FRAME:-odom}"
  "map_frame:=${MAP_FRAME:-map}"
  "use_sim_time:=${USE_SIM_TIME}"
)

if [[ -n "${DATABASE_PATH}" && "${DATABASE_PATH}" != "<"*">" ]]; then
  launch_args+=("database_path:=${DATABASE_PATH}")
fi

ros2 launch launch/rtabmap_mapping.launch.py \
  "${launch_args[@]}"
