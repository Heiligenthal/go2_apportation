#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTAINER_NAME="${CONTAINER_NAME:-go2_board_runtime}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
ARTIFACT_DIR="${ROOT_DIR}/artifacts/bringup/${TIMESTAMP}"
mkdir -p "${ARTIFACT_DIR}"

SUMMARY_LOG="${ARTIFACT_DIR}/summary.log"
RUNTIME_STDOUT="${ARTIFACT_DIR}/00_runtime_start.stdout.log"
RUNTIME_STDERR="${ARTIFACT_DIR}/00_runtime_start.stderr.log"
BRINGUP_STDOUT="${ARTIFACT_DIR}/01_board_description.stdout.log"
BRINGUP_STDERR="${ARTIFACT_DIR}/01_board_description.stderr.log"
INNER_SCRIPT="${ARTIFACT_DIR}/board_description_inner.sh"

log() {
  local msg="$1"
  printf '[%s] %s\n' "$(date +%H:%M:%S)" "${msg}" | tee -a "${SUMMARY_LOG}"
}

container_is_running() {
  docker ps --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"
}

start_runtime_container_if_needed() {
  if container_is_running; then
    log "Container '${CONTAINER_NAME}' already running; reusing it."
    return 0
  fi

  log "Starting runtime container '${CONTAINER_NAME}' via run_board_runtime.sh --run 'sleep infinity'."
  (
    cd "${ROOT_DIR}"
    scripts/bringup/run_board_runtime.sh --run "sleep infinity"
  ) >"${RUNTIME_STDOUT}" 2>"${RUNTIME_STDERR}" &

  local waited=0
  while (( waited < 30 )); do
    if container_is_running; then
      log "Container '${CONTAINER_NAME}' is running."
      return 0
    fi
    sleep 1
    waited=$((waited + 1))
  done

  log "FAIL: container '${CONTAINER_NAME}' did not start within 30s."
  log "Inspect ${RUNTIME_STDERR} for details."
  return 1
}

write_inner_script() {
  cat > "${INNER_SCRIPT}" <<'EOS'
#!/usr/bin/env bash
set -euo pipefail

# ROS setup scripts may access unset env vars; source them with nounset disabled.
restore_nounset=0
if [[ $- == *u* ]]; then
  restore_nounset=1
fi
set +u
source /opt/ros/humble/setup.bash
set -u

cd /workspace/repo

if [[ ! -f /workspace/repo/install_container/setup.bash ]]; then
  echo "[run_board_description_in_container] INFO: install_container/setup.bash missing; running colcon build." >&2
  colcon build --build-base build_container --install-base install_container
fi

set +u
if [[ -f /workspace/repo/install_container/setup.bash ]]; then
  source /workspace/repo/install_container/setup.bash
elif [[ -f /workspace/repo/install/setup.bash ]]; then
  source /workspace/repo/install/setup.bash
else
  echo "[run_board_description_in_container] ERROR: no workspace overlay found (install_container/setup.bash or install/setup.bash)." >&2
  exit 1
fi
if [[ "${restore_nounset}" -eq 1 ]]; then
  set -u
fi

if ! ros2 pkg prefix go2_tf_tools >/dev/null 2>&1; then
  echo "[run_board_description_in_container] ERROR: ros2 cannot resolve package go2_tf_tools after sourcing overlay." >&2
  exit 1
fi

echo "[run_board_description_in_container] PASS: go2_tf_tools resolved. Starting board_description launch." >&2
exec ros2 launch launch/board_description.launch.py
EOS
  chmod +x "${INNER_SCRIPT}"
}

main() {
  log "Artifacts: ${ARTIFACT_DIR}"
  start_runtime_container_if_needed
  write_inner_script

  log "Launching board_description inside container '${CONTAINER_NAME}'."
  if docker exec "${CONTAINER_NAME}" bash -lc "/workspace/repo/artifacts/bringup/${TIMESTAMP}/board_description_inner.sh" >"${BRINGUP_STDOUT}" 2>"${BRINGUP_STDERR}"; then
    log "PASS: board_description launch finished cleanly."
  else
    rc=$?
    log "FAIL: board_description launch failed (rc=${rc})."
    log "Inspect ${BRINGUP_STDERR} for details."
    exit "${rc}"
  fi
}

main "$@"
