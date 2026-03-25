#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT_DIR="${ROOT_DIR}/artifacts/bags/calibration_${TIMESTAMP}"
WITH_SCAN=0

usage() {
  cat <<'USAGE'
Usage:
  scripts/rtabmap/record_calibration_bag.sh [--with-scan]

Options:
  --with-scan  Additionally record /scan
  -h, --help   Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-scan)
      WITH_SCAN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[record_calibration_bag] ERROR: unknown argument '$1'." >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v ros2 >/dev/null 2>&1; then
  echo "[record_calibration_bag] ERROR: ros2 CLI not found in PATH." >&2
  exit 1
fi

mkdir -p "$(dirname "${OUTPUT_DIR}")"

TOPICS=(
  "/camera/realsense2_camera/color/image_raw"
  "/camera/realsense2_camera/aligned_depth_to_color/image_raw"
  "/camera/realsense2_camera/color/camera_info"
  "/utlidar/robot_odom"
  "/tf"
  "/tf_static"
)

if [[ "${WITH_SCAN}" -eq 1 ]]; then
  TOPICS+=("/scan")
fi

echo "[record_calibration_bag] Recording topics:"
for topic in "${TOPICS[@]}"; do
  echo "  ${topic}"
done
echo "[record_calibration_bag] Output directory:"
echo "  ${OUTPUT_DIR}"

ros2 bag record -o "${OUTPUT_DIR}" "${TOPICS[@]}"
