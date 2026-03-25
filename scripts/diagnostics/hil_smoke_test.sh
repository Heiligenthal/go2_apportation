#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
ARTIFACT_DIR="${ROOT_DIR}/artifacts/hil_smoke/${TIMESTAMP}"
INNER_SCRIPT_HOST="${ARTIFACT_DIR}/hil_inner.sh"
SUMMARY_LOG="${ARTIFACT_DIR}/summary.log"

mkdir -p "${ARTIFACT_DIR}"

log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "${SUMMARY_LOG}"
}

if ! command -v docker >/dev/null 2>&1; then
  log "FAIL: docker CLI not found."
  exit 1
fi

if [[ ! -x "${ROOT_DIR}/scripts/bringup/run_board_runtime.sh" ]]; then
  log "FAIL: scripts/bringup/run_board_runtime.sh is missing or not executable."
  exit 1
fi

cat >"${INNER_SCRIPT_HOST}" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/workspace/repo"
ARTIFACT_DIR="$1"
TOPICS_FILE="${ROOT_DIR}/config/runtime_topics.yaml"
FAILURES=0
REALSENSE_PID=""
BOARD_DESC_PID=""

mkdir -p "${ARTIFACT_DIR}"

step_log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "${ARTIFACT_DIR}/summary.log"
}

run_capture() {
  local step="$1"
  local cmd="$2"
  local stdout_log="${ARTIFACT_DIR}/${step}.stdout.log"
  local stderr_log="${ARTIFACT_DIR}/${step}.stderr.log"

  set +e
  bash -lc "${cmd}" >"${stdout_log}" 2>"${stderr_log}"
  local rc=$?
  set -e

  if [[ ${rc} -ne 0 ]]; then
    step_log "FAIL ${step} (rc=${rc})"
    FAILURES=$((FAILURES + 1))
    return ${rc}
  fi

  step_log "PASS ${step}"
  return 0
}

supports_echo_sensor_qos() {
  ros2 topic echo --help 2>&1 | grep -q -- "--qos-reliability"
}

echo_once_cmd() {
  local topic="$1"
  local prefer_sensor_qos="$2"
  local cmd="ros2 topic echo --once ${topic}"
  if [[ "${prefer_sensor_qos}" == "1" ]] && supports_echo_sensor_qos; then
    cmd="ros2 topic echo --once --qos-reliability best_effort --qos-durability volatile ${topic}"
  fi
  printf '%s' "${cmd}"
}

tf_pair_in_file() {
  local tf_file="$1"
  local parent="$2"
  local child="$3"
  awk -v p="${parent}" -v c="${child}" '
    $0 ~ ("frame_id:[[:space:]]*" p "$") {seen_parent=1}
    seen_parent && $0 ~ ("child_frame_id:[[:space:]]*" c "$") {found=1; exit}
    END {exit(found ? 0 : 1)}
  ' "${tf_file}"
}

wait_for_tf_pair() {
  local parent="$1"
  local child="$2"
  local timeout_sec="$3"
  local attempt=0
  local start_ts
  local elapsed
  local attempt_stdout
  local attempt_stderr
  local last_tf_stdout="${ARTIFACT_DIR}/07a_wait_tf_last.stdout.log"
  local last_tf_stderr="${ARTIFACT_DIR}/07a_wait_tf_last.stderr.log"
  local summary_file="${ARTIFACT_DIR}/07a_wait_tf.summary.log"

  start_ts="$(date +%s)"
  : >"${summary_file}"

  while true; do
    elapsed=$(( $(date +%s) - start_ts ))
    if (( elapsed >= timeout_sec )); then
      step_log "FAIL 07a_wait_tf_pair timeout after ${elapsed}s (parent=${parent}, child=${child})"
      if [[ -f "${last_tf_stdout}" ]]; then
        step_log "Last /tf snippet (${last_tf_stdout}):"
        sed -n '1,80p' "${last_tf_stdout}" | tee -a "${ARTIFACT_DIR}/summary.log"
      fi
      step_log "Hint: verify odom_to_tf_broadcaster logs (topic/frames/stamp_source)."
      return 1
    fi

    attempt=$((attempt + 1))
    attempt_stdout="${ARTIFACT_DIR}/07a_wait_tf_attempt_${attempt}.stdout.log"
    attempt_stderr="${ARTIFACT_DIR}/07a_wait_tf_attempt_${attempt}.stderr.log"

    set +e
    timeout 3s ros2 topic echo --once /tf >"${attempt_stdout}" 2>"${attempt_stderr}"
    local rc=$?
    set -e

    cp -f "${attempt_stdout}" "${last_tf_stdout}" 2>/dev/null || true
    cp -f "${attempt_stderr}" "${last_tf_stderr}" 2>/dev/null || true

    printf '[%s] attempt=%d elapsed=%ds rc=%d\n' "$(date +%H:%M:%S)" "${attempt}" "${elapsed}" "${rc}" >>"${summary_file}"

    if [[ ${rc} -eq 0 ]] && tf_pair_in_file "${attempt_stdout}" "${parent}" "${child}"; then
      step_log "PASS 07a_wait_tf_pair found ${parent}->${child} after ${attempt} attempts (${elapsed}s)."
      return 0
    fi

    sleep 1
  done
}

cleanup() {
  set +e
  if [[ -n "${REALSENSE_PID}" ]] && kill -0 "${REALSENSE_PID}" 2>/dev/null; then
    kill "${REALSENSE_PID}" >/dev/null 2>&1 || true
    wait "${REALSENSE_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${BOARD_DESC_PID}" ]] && kill -0 "${BOARD_DESC_PID}" 2>/dev/null; then
    kill "${BOARD_DESC_PID}" >/dev/null 2>&1 || true
    wait "${BOARD_DESC_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

step_log "HIL smoke inner test started."

# ROS setup scripts may read unset vars; temporarily disable nounset while sourcing.
restore_nounset=0
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
  step_log "WARN: ${ROOT_DIR}/install_container/setup.bash and ${ROOT_DIR}/install/setup.bash not found."
fi
if [[ ${restore_nounset} -eq 1 ]]; then
  set -u
fi

step_log "Starting launch A: realsense_board.launch.py"
ros2 launch launch/realsense_board.launch.py \
  >"${ARTIFACT_DIR}/01_realsense_launch.stdout.log" \
  2>"${ARTIFACT_DIR}/01_realsense_launch.stderr.log" &
REALSENSE_PID=$!

step_log "Starting launch B: board_description.launch.py"
ros2 launch launch/board_description.launch.py \
  >"${ARTIFACT_DIR}/02_board_description_launch.stdout.log" \
  2>"${ARTIFACT_DIR}/02_board_description_launch.stderr.log" &
BOARD_DESC_PID=$!

step_log "Waiting up to 20s for startup."
sleep 20

run_capture "03_topic_list_all" "ros2 topic list"

TOPIC_LIST_FILE="${ARTIFACT_DIR}/03_topic_list_all.stdout.log"
if [[ ! -f "${TOPIC_LIST_FILE}" ]]; then
  step_log "FAIL missing topic list output."
  FAILURES=$((FAILURES + 1))
fi

if grep -Fxq "/tf" "${TOPIC_LIST_FILE}"; then
  step_log "PASS topic /tf present"
else
  step_log "FAIL topic /tf missing"
  FAILURES=$((FAILURES + 1))
fi

if grep -Fxq "/tf_static" "${TOPIC_LIST_FILE}"; then
  step_log "PASS topic /tf_static present"
else
  step_log "FAIL topic /tf_static missing"
  FAILURES=$((FAILURES + 1))
fi

if grep -Fxq "/utlidar/robot_odom" "${TOPIC_LIST_FILE}"; then
  step_log "PASS topic /utlidar/robot_odom present"
else
  step_log "FAIL topic /utlidar/robot_odom missing (required by current board_minimal contract)"
  FAILURES=$((FAILURES + 1))
fi

read_runtime_topic() {
  local key="$1"
  if [[ ! -f "${TOPICS_FILE}" ]]; then
    return 0
  fi
  awk -F': *' -v key="${key}" '$1 ~ "^[[:space:]]*"key"$" {print $2}' "${TOPICS_FILE}" \
    | tr -d '"' \
    | tail -n 1
}

is_placeholder() {
  local value="$1"
  [[ -z "${value}" || "${value}" == "<"*">" ]]
}

RUNTIME_RGB="$(read_runtime_topic rgb_topic)"
RUNTIME_DEPTH="$(read_runtime_topic depth_topic)"
RUNTIME_CAMERA_INFO="$(read_runtime_topic camera_info_topic)"

RGB_TOPIC=""
CAMERA_INFO_TOPIC=""
DEPTH_TOPIC=""

if ! is_placeholder "${RUNTIME_RGB}" && grep -Fxq "${RUNTIME_RGB}" "${TOPIC_LIST_FILE}"; then
  RGB_TOPIC="${RUNTIME_RGB}"
fi
if ! is_placeholder "${RUNTIME_CAMERA_INFO}" && grep -Fxq "${RUNTIME_CAMERA_INFO}" "${TOPIC_LIST_FILE}"; then
  CAMERA_INFO_TOPIC="${RUNTIME_CAMERA_INFO}"
fi
if ! is_placeholder "${RUNTIME_DEPTH}" && grep -Fxq "${RUNTIME_DEPTH}" "${TOPIC_LIST_FILE}"; then
  DEPTH_TOPIC="${RUNTIME_DEPTH}"
fi

if [[ -z "${RGB_TOPIC}" ]]; then
  RGB_TOPIC="$(grep -E '/color/image_raw$|/image_raw$' "${TOPIC_LIST_FILE}" | head -n 1 || true)"
fi
if [[ -z "${CAMERA_INFO_TOPIC}" ]]; then
  CAMERA_INFO_TOPIC="$(grep -E '/camera_info$' "${TOPIC_LIST_FILE}" | head -n 1 || true)"
fi
if [[ -z "${DEPTH_TOPIC}" ]]; then
  DEPTH_TOPIC="$(grep -E '/aligned_depth.*image_raw$|/depth.*image_raw$' "${TOPIC_LIST_FILE}" | head -n 1 || true)"
fi

step_log "Selected topics: rgb='${RGB_TOPIC:-<none>}' camera_info='${CAMERA_INFO_TOPIC:-<none>}' depth='${DEPTH_TOPIC:-<none>}'"

if [[ -z "${RGB_TOPIC}" ]]; then
  step_log "FAIL no RGB image topic found."
  FAILURES=$((FAILURES + 1))
fi
if [[ -z "${CAMERA_INFO_TOPIC}" ]]; then
  step_log "FAIL no camera_info topic found."
  FAILURES=$((FAILURES + 1))
fi
if [[ -z "${DEPTH_TOPIC}" ]]; then
  step_log "WARN no depth image topic found (optional for smoke)."
fi

if [[ -n "${RGB_TOPIC}" ]]; then
  run_capture "04_echo_rgb" "timeout 10s $(echo_once_cmd "${RGB_TOPIC}" "1")"
fi

if [[ -n "${CAMERA_INFO_TOPIC}" ]]; then
  run_capture "05_echo_camera_info" "timeout 10s $(echo_once_cmd "${CAMERA_INFO_TOPIC}" "1")"
fi

if [[ -n "${DEPTH_TOPIC}" ]]; then
  run_capture "06_echo_depth_optional" "timeout 10s $(echo_once_cmd "${DEPTH_TOPIC}" "1")" || true
fi

if ! wait_for_tf_pair "odom" "base_link" 20; then
  FAILURES=$((FAILURES + 1))
fi

if (( FAILURES == 0 )); then
  set +e
  timeout 6s ros2 run tf2_ros tf2_echo odom base_link \
    >"${ARTIFACT_DIR}/07b_tf2_echo_odom_base_link.stdout.log" \
    2>"${ARTIFACT_DIR}/07b_tf2_echo_odom_base_link.stderr.log"
  tf_echo_rc=$?
  set -e
  if [[ ${tf_echo_rc} -ne 0 ]]; then
    step_log "WARN 07b_tf2_echo_odom_base_link_optional failed (rc=${tf_echo_rc}); publication already confirmed via /tf."
  else
    step_log "PASS 07b_tf2_echo_odom_base_link_optional"
  fi
fi

if [[ ${FAILURES} -eq 0 ]]; then
  step_log "HIL_SMOKE_RESULT=PASS"
  exit 0
fi

step_log "HIL_SMOKE_RESULT=FAIL failures=${FAILURES}"
exit 1
EOF

chmod +x "${INNER_SCRIPT_HOST}"

log "Artifacts directory: ${ARTIFACT_DIR}"
log "Starting Variant-A runtime container smoke test."

set +e
"${ROOT_DIR}/scripts/bringup/run_board_runtime.sh" \
  --run "/workspace/repo/artifacts/hil_smoke/${TIMESTAMP}/hil_inner.sh /workspace/repo/artifacts/hil_smoke/${TIMESTAMP}" \
  >"${ARTIFACT_DIR}/00_runtime_wrapper.stdout.log" \
  2>"${ARTIFACT_DIR}/00_runtime_wrapper.stderr.log"
RC=$?
set -e

if [[ ${RC} -ne 0 ]]; then
  log "FAIL: HIL smoke test returned rc=${RC}."
  log "See logs under ${ARTIFACT_DIR}"
  exit "${RC}"
fi

log "PASS: HIL smoke test completed."
log "See logs under ${ARTIFACT_DIR}"
