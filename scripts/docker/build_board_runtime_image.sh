#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
ARTIFACT_DIR="${ROOT_DIR}/artifacts/docker_build/${TIMESTAMP}"
STDOUT_LOG="${ARTIFACT_DIR}/docker_build.stdout.log"
STDERR_LOG="${ARTIFACT_DIR}/docker_build.stderr.log"
IMAGE_TAG="go2_board_runtime:humble"
DOCKERFILE_PATH="${ROOT_DIR}/docker/Dockerfile.board_runtime"
INCLUDED_PACKAGES="ros-humble-realsense2-camera ros-humble-rtabmap-ros ros-humble-slam-toolbox ros-humble-nav2-map-server ros-humble-pointcloud-to-laserscan"

mkdir -p "${ARTIFACT_DIR}"

if ! command -v docker >/dev/null 2>&1; then
  echo "[build_board_runtime_image] ERROR: docker CLI not found." >&2
  exit 1
fi

if [[ ! -f "${DOCKERFILE_PATH}" ]]; then
  echo "[build_board_runtime_image] ERROR: missing ${DOCKERFILE_PATH}." >&2
  exit 1
fi

build_cmd=(
  docker build
  -t "${IMAGE_TAG}"
  -f "${DOCKERFILE_PATH}"
  "${ROOT_DIR}"
)

echo "[build_board_runtime_image] Artifacts: ${ARTIFACT_DIR}"
echo "[build_board_runtime_image] Included ROS packages: ${INCLUDED_PACKAGES}"
echo "[build_board_runtime_image] Docker command:"
printf '  %q' "${build_cmd[@]}"
echo

set +e
"${build_cmd[@]}" >"${STDOUT_LOG}" 2>"${STDERR_LOG}"
rc=$?
set -e

if [[ ${rc} -ne 0 ]]; then
  echo "[build_board_runtime_image] FAIL: docker build returned rc=${rc}." >&2
  echo "[build_board_runtime_image] See logs: ${STDOUT_LOG} ${STDERR_LOG}" >&2
  exit "${rc}"
fi

echo "[build_board_runtime_image] PASS: built ${IMAGE_TAG}."
echo "[build_board_runtime_image] Logs: ${STDOUT_LOG} ${STDERR_LOG}"
