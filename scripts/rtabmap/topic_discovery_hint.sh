#!/usr/bin/env bash
set -euo pipefail

if ! command -v ros2 >/dev/null 2>&1; then
  echo "[ERROR] ros2 CLI not found in PATH." >&2
  exit 1
fi

echo "Candidate image/depth/camera_info topics:"
ros2 topic list | grep -E "(image_raw|aligned_depth|camera_info)" || true

echo
echo "Use selected topics with:"
echo "  ros2 launch launch/rtabmap_mapping.launch.py rgb_topic:=<...> depth_topic:=<...> camera_info_topic:=<...>"
echo "  ros2 launch launch/rtabmap_localization.launch.py rgb_topic:=<...> depth_topic:=<...> camera_info_topic:=<...> database_path:=<...>"
