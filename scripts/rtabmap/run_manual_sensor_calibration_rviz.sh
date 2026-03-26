#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RVIZ_CONFIG="${ROOT_DIR}/config/manual_sensor_calibration.rviz"

log() {
  printf '[run_manual_sensor_calibration_rviz] %s\n' "$*"
}

source_env() {
  local restore_nounset=0
  if [[ $- == *u* ]]; then
    restore_nounset=1
    set +u
  fi
  source /opt/ros/humble/setup.bash
  if [[ -f "${ROOT_DIR}/install_container/setup.bash" ]]; then
    source "${ROOT_DIR}/install_container/setup.bash"
  elif [[ -f "${ROOT_DIR}/install/setup.bash" ]]; then
    source "${ROOT_DIR}/install/setup.bash"
  else
    echo "[run_manual_sensor_calibration_rviz] ERROR: install_container/setup.bash or install/setup.bash not found locally." >&2
    exit 1
  fi
  if [[ "${restore_nounset}" -eq 1 ]]; then
    set -u
  fi
}

if [[ ! -f "${RVIZ_CONFIG}" ]]; then
  echo "[run_manual_sensor_calibration_rviz] ERROR: missing RViz config ${RVIZ_CONFIG}." >&2
  exit 1
fi

export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"
source_env

if ! ros2 pkg executables rviz2 2>/dev/null | grep -Fq "rviz2"; then
  echo "[run_manual_sensor_calibration_rviz] ERROR: rviz2 is not available in the local Ubuntu-laptop environment." >&2
  exit 1
fi

go2_prefix="$(ros2 pkg prefix go2_description 2>/dev/null || true)"
if [[ -z "${go2_prefix}" ]]; then
  echo "[run_manual_sensor_calibration_rviz] ERROR: go2_description is not available in the local Ubuntu-laptop environment." >&2
  echo "[run_manual_sensor_calibration_rviz] Robot Model meshes will not resolve without a locally sourced workspace containing go2_description." >&2
  exit 1
fi

if [[ ! -f "${go2_prefix}/share/go2_description/dae/base.dae" ]]; then
  echo "[run_manual_sensor_calibration_rviz] ERROR: go2_description mesh asset missing at ${go2_prefix}/share/go2_description/dae/base.dae" >&2
  exit 1
fi

log "ROS_DOMAIN_ID=${ROS_DOMAIN_ID}"
log "Using local go2_description from ${go2_prefix}"
log "Using RViz config ${RVIZ_CONFIG}"
log "Expected live topics: /manual_calibration/lidar_cloud and /manual_calibration/camera_cloud"
exec ros2 run rviz2 rviz2 -d "${RVIZ_CONFIG}"
