#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ARTIFACT_ROOT="${ROOT_DIR}/artifacts/checks"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${ARTIFACT_ROOT}/${TIMESTAMP}"
SUMMARY_LOG="${RUN_DIR}/summary.log"

IMAGE="${IMAGE:-ros:humble-ros-base}"
CONTAINER_NAME="${CONTAINER_NAME:-go2_humble_checks}"
ENABLE_PRIVILEGED="${ENABLE_PRIVILEGED:-0}"
REUSE_RUNNING_CONTAINER="${REUSE_RUNNING_CONTAINER:-1}"
KEEP_CONTAINER="${KEEP_CONTAINER:-0}"
RUN_AS_ROOT=0

STARTED_CONTAINER=0

mkdir -p "${RUN_DIR}"

log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "${SUMMARY_LOG}"
}

cleanup() {
  if [[ "${KEEP_CONTAINER}" == "1" ]]; then
    log "KEEP_CONTAINER=1 -> leaving container '${CONTAINER_NAME}' running."
    return
  fi

  if [[ "${STARTED_CONTAINER}" -eq 1 ]]; then
    log "Stopping container '${CONTAINER_NAME}'."
    docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

if ! command -v docker >/dev/null 2>&1; then
  log "ERROR: docker CLI not found."
  exit 1
fi

usage() {
  cat <<'EOF'
Usage:
  scripts/docker/run_checks_in_container.sh [--as-root] [-h|--help]

Options:
  --as-root   Container ohne --user starten (Default: Host-UID/GID).
  -h, --help  Hilfe anzeigen.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --as-root)
      RUN_AS_ROOT=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

extra_args=()
if [[ "${ENABLE_PRIVILEGED}" == "1" ]]; then
  extra_args+=(--privileged)
fi

run_user_args=()
run_env_args=()
if [[ "${RUN_AS_ROOT}" == "0" ]]; then
  run_user_args+=(--user "$(id -u):$(id -g)")
  run_env_args+=(-e "HOME=/tmp")
fi

container_running() {
  docker ps --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"
}

container_exists() {
  docker ps -a --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"
}

ensure_container() {
  if [[ "${REUSE_RUNNING_CONTAINER}" == "1" ]] && container_running; then
    log "Reusing running container '${CONTAINER_NAME}'."
    return
  fi

  if container_exists; then
    log "Removing existing non-reused container '${CONTAINER_NAME}'."
    docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
  fi

  log "Starting container '${CONTAINER_NAME}' from image '${IMAGE}'."
  docker run -d --rm \
    --network host \
    "${extra_args[@]}" \
    "${run_user_args[@]}" \
    "${run_env_args[@]}" \
    -v "${ROOT_DIR}:/workspace/repo" \
    -w /workspace/repo \
    --name "${CONTAINER_NAME}" \
    "${IMAGE}" \
    bash -lc "sleep infinity" >/dev/null
  STARTED_CONTAINER=1
}

run_step() {
  local step_name="$1"
  local cmd="$2"
  local stdout_log="${RUN_DIR}/${step_name}.stdout.log"
  local stderr_log="${RUN_DIR}/${step_name}.stderr.log"

  log "Running ${step_name}"
  set +e
  docker exec "${CONTAINER_NAME}" bash -lc "${cmd}" >"${stdout_log}" 2>"${stderr_log}"
  local rc=$?
  set -e

  if [[ ${rc} -ne 0 ]]; then
    log "FAIL ${step_name} (rc=${rc})"
    log "stdout: ${stdout_log}"
    log "stderr: ${stderr_log}"
    tail -n 40 "${stderr_log}" >>"${SUMMARY_LOG}" || true
    exit ${rc}
  fi

  log "PASS ${step_name}"
}

log "Artifacts directory: ${RUN_DIR}"
ensure_container

run_step \
  "01_colcon_build" \
  "set -eo pipefail; source /opt/ros/humble/setup.bash; colcon --log-base log_container build --build-base build_container --install-base install_container"

run_step \
  "02_pytest" \
  "set -eo pipefail; source /opt/ros/humble/setup.bash; \
   if [ -f install_container/local_setup.bash ]; then \
     source install_container/local_setup.bash; \
   elif [ -f install_container/setup.bash ]; then \
     source install_container/setup.bash; \
   else \
     echo '[runner] missing install_container setup script' >&2; \
     exit 3; \
   fi; \
   overlay_python_paths=\$(find install_container -type d \\( -path '*/dist-packages' -o -path '*/site-packages' \\) | paste -sd: -); \
   if [ -n \"\${overlay_python_paths}\" ]; then \
     export PYTHONPATH=\"\${overlay_python_paths}:\${PYTHONPATH:-}\"; \
   fi; \
   export PYTHONPATH=\"/workspace/repo:\${PYTHONPATH:-}\"; \
   python3 -c \"import go2_apportation_msgs.action, go2_apportation_msgs.srv\"; \
   cd /workspace/repo/tests; \
   python3 -m pytest -q"

log "All checks passed."
