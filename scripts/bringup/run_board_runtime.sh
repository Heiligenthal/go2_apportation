#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

DEFAULT_IMAGE="go2_board_runtime:humble"
FALLBACK_IMAGE="ros:humble-ros-base"
IMAGE="${IMAGE:-}"
CONTAINER_NAME="${CONTAINER_NAME:-go2_board_runtime}"
ENABLE_PRIVILEGED="${ENABLE_PRIVILEGED:-0}"
ROS_DOMAIN_ID_VALUE="${ROS_DOMAIN_ID:-0}"

RUN_COMMAND=""

usage() {
  cat <<'EOF'
Usage:
  scripts/bringup/run_board_runtime.sh [--run "<command>"] [-h|--help]

Modes:
  default         Start interactive runtime shell with ROS environment sourced.
  --run "<cmd>"   Run command non-interactively in runtime container.

Environment:
  IMAGE=<tag>                 Container image override
  CONTAINER_NAME=go2_board_runtime
  ENABLE_PRIVILEGED=0|1
  ROS_DOMAIN_ID=<int>         Defaults to 0 if unset
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run)
      if [[ $# -lt 2 ]]; then
        echo "[run_board_runtime] ERROR: --run requires a command string." >&2
        exit 2
      fi
      RUN_COMMAND="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[run_board_runtime] ERROR: unknown argument '$1'." >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "${IMAGE}" ]]; then
  if docker image inspect "${DEFAULT_IMAGE}" >/dev/null 2>&1; then
    IMAGE="${DEFAULT_IMAGE}"
  else
    IMAGE="${FALLBACK_IMAGE}"
    echo "[run_board_runtime] WARN: ${DEFAULT_IMAGE} not found; camera driver may be missing. Run scripts/docker/build_board_runtime_image.sh"
  fi
fi

docker_args=(
  --rm
  --network host
  --ipc host
  --user "$(id -u):$(id -g)"
  -e "HOME=/tmp"
  -e "ROS_DOMAIN_ID=${ROS_DOMAIN_ID_VALUE}"
  -v "${ROOT_DIR}:/workspace/repo"
  -w /workspace/repo
  --name "${CONTAINER_NAME}"
  --device=/dev/bus/usb:/dev/bus/usb
)

if [[ "${ENABLE_PRIVILEGED}" == "1" ]]; then
  docker_args+=(--privileged)
fi

shopt -s nullglob
video_devices=(/dev/video*)
shopt -u nullglob
if [[ ${#video_devices[@]} -gt 0 ]]; then
  for dev in "${video_devices[@]}"; do
    if [[ -c "${dev}" ]]; then
      docker_args+=(--device="${dev}:${dev}")
    fi
  done
else
  echo "[run_board_runtime] INFO: no /dev/video* devices found on host."
fi

if [[ -z "${RUN_COMMAND}" ]]; then
  container_entry='
    set -eo pipefail
    source /opt/ros/humble/setup.bash
    if [[ -f install_container/setup.bash ]]; then
      source install_container/setup.bash
    elif [[ -f install/setup.bash ]]; then
      source install/setup.bash
    else
      echo "[run_board_runtime] WARN: install_container/setup.bash and install/setup.bash not found. Build workspace first (colcon build)." >&2
    fi
    set -u
    exec bash
  '
  tty_args=(-it)
else
  container_entry="
    set -eo pipefail
    source /opt/ros/humble/setup.bash
    if [[ -f install_container/setup.bash ]]; then
      source install_container/setup.bash
    elif [[ -f install/setup.bash ]]; then
      source install/setup.bash
    else
      echo \"[run_board_runtime] WARN: install_container/setup.bash and install/setup.bash not found. Build workspace first (colcon build).\" >&2
    fi
    set -u
    ${RUN_COMMAND}
  "
  tty_args=()
fi

docker_cmd=(docker run "${tty_args[@]}" "${docker_args[@]}" "${IMAGE}" bash -lc "${container_entry}")

echo "[run_board_runtime] Docker command:"
printf '  %q' "${docker_cmd[@]}"
echo

"${docker_cmd[@]}"
