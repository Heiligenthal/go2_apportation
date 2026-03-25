#!/usr/bin/env bash
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "[install_realsense_deps] ERROR: run as root inside container." >&2
  echo "[install_realsense_deps] Hint: use --user root or rerun with sudo." >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

echo "[install_realsense_deps] apt-get update"
apt-get update

required_pkgs=(
  ros-humble-realsense2-camera
)

optional_pkg="librealsense2-utils"

echo "[install_realsense_deps] Installing required packages: ${required_pkgs[*]}"
apt-get install -y --no-install-recommends "${required_pkgs[@]}"

resolved_optional=()
if apt-cache policy "${optional_pkg}" | grep -q "Candidate:"; then
  if apt-cache policy "${optional_pkg}" | grep -q "Candidate: (none)"; then
    echo "[install_realsense_deps] INFO: optional package ${optional_pkg} has no candidate in current apt repos."
  else
    resolved_optional+=("${optional_pkg}")
  fi
else
  echo "[install_realsense_deps] INFO: optional package ${optional_pkg} not found in current apt repositories."
fi

echo "[install_realsense_deps] Resolved package set:"
echo "  required: ${required_pkgs[*]}"
if [[ ${#resolved_optional[@]} -gt 0 ]]; then
  echo "  optional: ${resolved_optional[*]}"
  apt-get install -y --no-install-recommends "${resolved_optional[@]}"
else
  echo "  optional: (none)"
fi

echo "[install_realsense_deps] Done."
