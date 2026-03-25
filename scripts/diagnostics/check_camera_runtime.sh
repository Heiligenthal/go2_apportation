#!/usr/bin/env bash
set -euo pipefail

if ! command -v ros2 >/dev/null 2>&1; then
  echo "[check_camera_runtime] ros2 CLI not found in PATH."
  echo "[check_camera_runtime] Hint: source /opt/ros/humble/setup.bash (and workspace install/setup.bash)."
  exit 0
fi

echo "[check_camera_runtime] Realsense-like nodes:"
if ! ros2 node list 2>/dev/null | grep -i realsense; then
  echo "  (none detected)"
fi

echo
echo "[check_camera_runtime] Image/Depth/CameraInfo topics (head):"
if ! ros2 topic list 2>/dev/null | grep -E "image|depth|camera_info" | head -n 120; then
  echo "  (none detected)"
fi

echo
echo "[check_camera_runtime] Hints:"
echo "  - If no realsense node: start 'ros2 launch launch/realsense_board.launch.py'."
echo "  - If no topics: check USB passthrough (/dev/bus/usb, /dev/video*) and driver package installation."
