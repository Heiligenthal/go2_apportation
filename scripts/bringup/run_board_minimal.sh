#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IMAGE="${IMAGE:-ros:humble-ros-base}"
CONTAINER_NAME="${CONTAINER_NAME:-go2_board_minimal}"
ENABLE_PRIVILEGED="${ENABLE_PRIVILEGED:-0}"

extra_args=()
if [[ "${ENABLE_PRIVILEGED}" == "1" ]]; then
  extra_args+=(--privileged)
fi

docker run --rm -it \
  --network host \
  "${extra_args[@]}" \
  -v "${ROOT_DIR}:/workspace/repo" \
  -w /workspace/repo \
  --name "${CONTAINER_NAME}" \
  "${IMAGE}" \
  bash -lc '
    set -euo pipefail
    source /opt/ros/humble/setup.bash
    if [[ -f install/setup.bash ]]; then
      source install/setup.bash
    else
      echo "[run_board_minimal] WARN: install/setup.bash not found. Build workspace first (colcon build)." >&2
    fi
    ros2 launch launch/board_minimal.launch.py
  '

