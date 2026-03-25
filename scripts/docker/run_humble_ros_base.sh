#!/usr/bin/env bash
set -euo pipefail

IMAGE="${IMAGE:-ros:humble-ros-base}"
CONTAINER_NAME="${CONTAINER_NAME:-go2_humble_cli}"
WORKSPACE_DIR="${WORKSPACE_DIR:-$PWD}"
ENABLE_PRIVILEGED="${ENABLE_PRIVILEGED:-0}"

extra_args=()
if [[ "${ENABLE_PRIVILEGED}" == "1" ]]; then
  extra_args+=(--privileged)
fi

docker run --rm -it \
  --network host \
  "${extra_args[@]}" \
  -v "${WORKSPACE_DIR}:/workspace" \
  --name "${CONTAINER_NAME}" \
  "${IMAGE}" \
  bash
