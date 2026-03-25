#!/usr/bin/env bash
set -eo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO_CASE="${DEMO_CASE:-nav_success}"
BACKEND="${BACKEND:-ros}"
CHECK_UNKNOWN_GUARDS="${CHECK_UNKNOWN_GUARDS:-0}"
INITIAL_STATE="${INITIAL_STATE:-SEARCH_OBJECT_GLOBAL}"
INITIAL_MODE="${INITIAL_MODE:-}"
EVENT_NAME="${EVENT_NAME:-object_detected}"
ENABLE_REAL_MOTION="${ENABLE_REAL_MOTION:-false}"
ENABLE_DEMO_POSE="${ENABLE_DEMO_POSE:-false}"
NAV2_ACTION_NAME="${NAV2_ACTION_NAME:-/navigate_to_pose}"

SCENARIO_NAV2="${SCENARIO_NAV2:-}"
SCENARIO_PICK="${SCENARIO_PICK:-}"
SCENARIO_RELEASE="${SCENARIO_RELEASE:-}"
NAV_RESULT_DELAY_S="${NAV_RESULT_DELAY_S:-0.2}"
PICK_RESULT_DELAY_S="${PICK_RESULT_DELAY_S:-0.3}"
RELEASE_RESULT_DELAY_S="${RELEASE_RESULT_DELAY_S:-0.1}"

LOG_DIR="${LOG_DIR:-/tmp/go2_mock_demo_${DEMO_CASE}}"
mkdir -p "${LOG_DIR}"

source /opt/ros/humble/setup.bash
source "${ROOT_DIR}/install/setup.bash"
set -u

export ROS_LOG_DIR="${LOG_DIR}/ros"
mkdir -p "${ROS_LOG_DIR}"

NAV_LOG="${LOG_DIR}/mock_nav2.log"
MANIP_LOG="${LOG_DIR}/mock_manip.log"
ORCH_LOG="${LOG_DIR}/orchestrator.log"
ACTIONS_LOG="${LOG_DIR}/actions.txt"
SERVICES_LOG="${LOG_DIR}/services.txt"
LAST_STATUS_JSON=""

fail() {
  echo "[demo][FAIL] $1"
  exit 1
}

warn() {
  echo "[demo][WARN] $1"
}

cleanup() {
  set +e
  [[ -n "${ORCH_PID:-}" ]] && kill "${ORCH_PID}" >/dev/null 2>&1
  [[ -n "${MANIP_PID:-}" ]] && kill "${MANIP_PID}" >/dev/null 2>&1
  [[ -n "${NAV_PID:-}" ]] && kill "${NAV_PID}" >/dev/null 2>&1
}
trap cleanup EXIT

set_case_defaults() {
  case "${DEMO_CASE}" in
    nav_success)
      [[ -z "${SCENARIO_NAV2}" ]] && SCENARIO_NAV2="success"
      [[ -z "${SCENARIO_PICK}" ]] && SCENARIO_PICK="success"
      [[ -z "${SCENARIO_RELEASE}" ]] && SCENARIO_RELEASE="success"
      ;;
    nav_fail)
      [[ -z "${SCENARIO_NAV2}" ]] && SCENARIO_NAV2="fail"
      [[ -z "${SCENARIO_PICK}" ]] && SCENARIO_PICK="success"
      [[ -z "${SCENARIO_RELEASE}" ]] && SCENARIO_RELEASE="success"
      ;;
    nav_hang_cancel)
      [[ -z "${SCENARIO_NAV2}" ]] && SCENARIO_NAV2="hang"
      [[ -z "${SCENARIO_PICK}" ]] && SCENARIO_PICK="success"
      [[ -z "${SCENARIO_RELEASE}" ]] && SCENARIO_RELEASE="success"
      ;;
    pick_hang_cancel)
      [[ -z "${SCENARIO_NAV2}" ]] && SCENARIO_NAV2="success"
      [[ -z "${SCENARIO_PICK}" ]] && SCENARIO_PICK="hang"
      [[ -z "${SCENARIO_RELEASE}" ]] && SCENARIO_RELEASE="success"
      [[ -z "${INITIAL_MODE}" ]] && INITIAL_MODE="SEARCH"
      ;;
    real_nav2_goal_send)
      BACKEND="real_nav2"
      [[ -z "${SCENARIO_NAV2}" ]] && SCENARIO_NAV2="success"
      [[ -z "${SCENARIO_PICK}" ]] && SCENARIO_PICK="success"
      [[ -z "${SCENARIO_RELEASE}" ]] && SCENARIO_RELEASE="success"
      ENABLE_REAL_MOTION="true"
      ENABLE_DEMO_POSE="true"
      ;;
    real_nav2_cancel)
      BACKEND="real_nav2"
      [[ -z "${SCENARIO_NAV2}" ]] && SCENARIO_NAV2="hang"
      [[ -z "${SCENARIO_PICK}" ]] && SCENARIO_PICK="success"
      [[ -z "${SCENARIO_RELEASE}" ]] && SCENARIO_RELEASE="success"
      ENABLE_REAL_MOTION="true"
      ENABLE_DEMO_POSE="true"
      ;;
    real_nav2_auto_result_success)
      BACKEND="real_nav2"
      [[ -z "${SCENARIO_NAV2}" ]] && SCENARIO_NAV2="success"
      [[ -z "${SCENARIO_PICK}" ]] && SCENARIO_PICK="success"
      [[ -z "${SCENARIO_RELEASE}" ]] && SCENARIO_RELEASE="success"
      ENABLE_REAL_MOTION="true"
      ENABLE_DEMO_POSE="true"
      INITIAL_STATE="SEARCH_PERSON"
      EVENT_NAME="person_detected"
      ;;
    real_nav2_auto_result_fail)
      BACKEND="real_nav2"
      [[ -z "${SCENARIO_NAV2}" ]] && SCENARIO_NAV2="fail"
      [[ -z "${SCENARIO_PICK}" ]] && SCENARIO_PICK="success"
      [[ -z "${SCENARIO_RELEASE}" ]] && SCENARIO_RELEASE="success"
      ENABLE_REAL_MOTION="true"
      ENABLE_DEMO_POSE="true"
      INITIAL_STATE="SEARCH_PERSON"
      EVENT_NAME="person_detected"
      ;;
    *)
      fail "Unsupported DEMO_CASE='${DEMO_CASE}'. Use nav_success|nav_fail|nav_hang_cancel|pick_hang_cancel|real_nav2_goal_send|real_nav2_cancel|real_nav2_auto_result_success|real_nav2_auto_result_fail."
      ;;
  esac
}

wait_for_log() {
  local pattern="$1"
  local file="$2"
  local timeout_s="${3:-20}"

  local attempts=$((timeout_s * 5))
  local i
  for ((i = 0; i < attempts; i++)); do
    if [[ -f "${file}" ]] && grep -q "${pattern}" "${file}"; then
      return 0
    fi
    sleep 0.2
  done
  return 1
}

publish_event() {
  local event_name="$1"
  echo "[demo] publishing event ${event_name}"
  timeout --kill-after=2s 10s ros2 topic pub /orchestrator/event std_msgs/msg/String "{data: ${event_name}}" -1 >/dev/null
}

extract_status_json() {
  local raw_file="$1"
  local json_file="$2"

  python3 - <<'PY' "${raw_file}" "${json_file}"
import json
import re
import sys
from pathlib import Path

raw_path = Path(sys.argv[1])
json_path = Path(sys.argv[2])
text = raw_path.read_text(encoding="utf-8")
match = re.search(r"data:\s*'(.*)'", text, flags=re.DOTALL)
if not match:
    print("[demo][FAIL] could not parse /orchestrator/status payload")
    sys.exit(2)

payload = match.group(1)
try:
    parsed = json.loads(payload)
except json.JSONDecodeError as exc:
    print(f"[demo][FAIL] status JSON decode failed: {exc}")
    sys.exit(3)

json_path.write_text(json.dumps(parsed, sort_keys=True), encoding="utf-8")
print(
    "[demo] status summary: backend={backend} state={state} event={event} "
    "dispatched={dispatched} unhandled={unhandled} unknown_guards={unknown} timeout_key={timeout}".format(
        backend=parsed.get("active_backend", parsed.get("backend", "")),
        state=parsed.get("state", ""),
        event=parsed.get("last_event", ""),
        dispatched=parsed.get("last_dispatched_actions_count", 0),
        unhandled=parsed.get("last_unhandled_tokens_count", 0),
        unknown=parsed.get("unknown_guard_count", 0),
        timeout=parsed.get("timeout_key", ""),
    )
)
PY
}

status_field() {
  local key="$1"
  local json_file="$2"
  python3 - <<'PY' "${key}" "${json_file}"
import json
import sys
from pathlib import Path

key = sys.argv[1]
data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
value = data.get(key, "")
print(value)
PY
}

status_list_contains() {
  local key="$1"
  local needle="$2"
  local json_file="$3"
  python3 - <<'PY' "${key}" "${needle}" "${json_file}"
import json
import sys
from pathlib import Path

key = sys.argv[1]
needle = sys.argv[2]
data = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
value = data.get(key, [])
if isinstance(value, list) and needle in value:
    print("1")
else:
    print("0")
PY
}

read_status() {
  local label="$1"
  local raw_file="${LOG_DIR}/status_${label}.raw"
  local json_file="${LOG_DIR}/status_${label}.json"

  echo "[demo] reading /orchestrator/status (${label})"
  timeout --kill-after=2s 12s ros2 topic echo /orchestrator/status --once --full-length >"${raw_file}"
  extract_status_json "${raw_file}" "${json_file}"
  LAST_STATUS_JSON="${json_file}"
}

wait_for_state() {
  local expected_state="$1"
  local timeout_s="${2:-20}"
  local label_prefix="${3:-wait_state}"

  local attempts=$((timeout_s * 3))
  local i
  for ((i = 0; i < attempts; i++)); do
    read_status "${label_prefix}_${i}"
    local state
    state="$(status_field "state" "${LAST_STATUS_JSON}")"
    if [[ "${state}" == "${expected_state}" ]]; then
      return 0
    fi
    sleep 0.2
  done
  return 1
}

validate_status_baseline() {
  local active_backend
  local dispatched_count
  local unknown_guard_count

  active_backend="$(status_field "active_backend" "${LAST_STATUS_JSON}")"
  dispatched_count="$(status_field "last_dispatched_actions_count" "${LAST_STATUS_JSON}")"
  unknown_guard_count="$(status_field "unknown_guard_count" "${LAST_STATUS_JSON}")"

  if [[ "${active_backend}" != "${BACKEND}" ]]; then
    fail "active_backend='${active_backend}' expected '${BACKEND}'"
  fi

  if [[ "${BACKEND}" == "ros" || "${BACKEND}" == "real_nav2" || "${BACKEND}" == "real" ]]; then
    if [[ "${dispatched_count}" -le 0 ]]; then
      fail "last_dispatched_actions_count must be > 0 for backend=${BACKEND}"
    fi
  fi

  if [[ "${CHECK_UNKNOWN_GUARDS}" == "1" && "${unknown_guard_count}" -gt 0 ]]; then
    warn "unknown_guard_count=${unknown_guard_count} (warning only)"
  fi
}

set_case_defaults

if [[ "${BACKEND}" == "ros" || "${BACKEND}" == "real_nav2" || "${BACKEND}" == "real" ]]; then
  echo "[demo] starting mock_nav2_server (scenario=${SCENARIO_NAV2})"
  ros2 run go2_apportation_mocks mock_nav2_server --ros-args \
    -p action_name:="${NAV2_ACTION_NAME}" \
    -p scenario:="${SCENARIO_NAV2}" \
    -p result_delay_s:="${NAV_RESULT_DELAY_S}" \
    -p accept_goal:=true \
    >"${NAV_LOG}" 2>&1 &
  NAV_PID=$!

  echo "[demo] starting mock_manipulation_server (pick=${SCENARIO_PICK}, release=${SCENARIO_RELEASE})"
  ros2 run go2_apportation_mocks mock_manipulation_server --ros-args \
    -p pick_scenario:="${SCENARIO_PICK}" \
    -p pick_result_delay_s:="${PICK_RESULT_DELAY_S}" \
    -p release_scenario:="${SCENARIO_RELEASE}" \
    -p release_result_delay_s:="${RELEASE_RESULT_DELAY_S}" \
    >"${MANIP_LOG}" 2>&1 &
  MANIP_PID=$!

  sleep 2
  kill -0 "${NAV_PID}" >/dev/null 2>&1 || fail "mock_nav2_server is not running"
  kill -0 "${MANIP_PID}" >/dev/null 2>&1 || fail "mock_manipulation_server is not running"
else
  echo "[demo] backend=${BACKEND}: skip mock server startup"
fi

echo "[demo] starting orchestrator_runtime (skills_backend=${BACKEND}, initial_state=${INITIAL_STATE})"
if [[ -n "${INITIAL_MODE}" ]]; then
  ros2 run go2_apportation_orchestrator orchestrator_runtime --ros-args \
    -p skills_backend:="${BACKEND}" \
    -p initial_state:="${INITIAL_STATE}" \
    -p initial_mode:="${INITIAL_MODE}" \
    -p enable_real_motion:="${ENABLE_REAL_MOTION}" \
    -p enable_demo_pose:="${ENABLE_DEMO_POSE}" \
    -p nav2_action_name:="${NAV2_ACTION_NAME}" \
    >"${ORCH_LOG}" 2>&1 &
else
  ros2 run go2_apportation_orchestrator orchestrator_runtime --ros-args \
    -p skills_backend:="${BACKEND}" \
    -p initial_state:="${INITIAL_STATE}" \
    -p enable_real_motion:="${ENABLE_REAL_MOTION}" \
    -p enable_demo_pose:="${ENABLE_DEMO_POSE}" \
    -p nav2_action_name:="${NAV2_ACTION_NAME}" \
    >"${ORCH_LOG}" 2>&1 &
fi
ORCH_PID=$!

sleep 2
kill -0 "${ORCH_PID}" >/dev/null 2>&1 || fail "orchestrator_runtime is not running"

echo "[demo] listing ROS action/service endpoints"
if ros2 --help | grep -q "[[:space:]]action[[:space:]]"; then
  timeout --kill-after=2s 10s ros2 action list >"${ACTIONS_LOG}" || true
else
  echo "[demo] ros2 action CLI plugin not available in this environment" >"${ACTIONS_LOG}"
fi
timeout --kill-after=2s 10s ros2 service list >"${SERVICES_LOG}" || true

publish_event "${EVENT_NAME}"
sleep 1
read_status "after_${EVENT_NAME}"
validate_status_baseline

case "${DEMO_CASE}" in
  nav_success)
    if [[ "${BACKEND}" == "ros" || "${BACKEND}" == "real_nav2" || "${BACKEND}" == "real" ]]; then
      wait_for_log "RESULT_SUCCEEDED" "${NAV_LOG}" 20 || fail "nav_success: no RESULT_SUCCEEDED in nav log"
    fi
    ;;
  nav_fail)
    if [[ "${BACKEND}" == "ros" || "${BACKEND}" == "real_nav2" || "${BACKEND}" == "real" ]]; then
      wait_for_log "RESULT_ABORTED" "${NAV_LOG}" 20 || fail "nav_fail: no RESULT_ABORTED in nav log"
    fi
    publish_event "nav_failed"
    sleep 1
    read_status "after_nav_failed"
    state_after_fail="$(status_field "state" "${LAST_STATUS_JSON}")"
    summary_after_fail="$(status_field "chosen_transition_summary" "${LAST_STATUS_JSON}")"
    [[ "${state_after_fail}" == "FAILSAFE_ABORT" ]] || fail "nav_fail: expected state FAILSAFE_ABORT, got ${state_after_fail}"
    [[ "${summary_after_fail}" == *"--nav_failed--> FAILSAFE_ABORT" ]] || fail "nav_fail: unexpected transition summary '${summary_after_fail}'"
    ;;
  nav_hang_cancel)
    if [[ "${BACKEND}" == "ros" || "${BACKEND}" == "real_nav2" || "${BACKEND}" == "real" ]]; then
      wait_for_log "GOAL_RECEIVED" "${NAV_LOG}" 20 || fail "nav_hang_cancel: no GOAL_RECEIVED in nav log"
    fi
    sleep 1
    publish_event "vc_abort"
    sleep 1
    read_status "after_vc_abort"
    state_after_abort="$(status_field "state" "${LAST_STATUS_JSON}")"
    event_after_abort="$(status_field "last_event" "${LAST_STATUS_JSON}")"
    [[ "${state_after_abort}" == "IDLE" ]] || fail "nav_hang_cancel: expected state IDLE, got ${state_after_abort}"
    [[ "${event_after_abort}" == "vc_abort" ]] || fail "nav_hang_cancel: expected last_event vc_abort, got ${event_after_abort}"
    if [[ "${BACKEND}" == "ros" || "${BACKEND}" == "real_nav2" || "${BACKEND}" == "real" ]]; then
      wait_for_log "CANCEL_RECEIVED" "${NAV_LOG}" 20 || fail "nav_hang_cancel: no CANCEL_RECEIVED in nav log"
      wait_for_log "RESULT_CANCELED" "${NAV_LOG}" 20 || fail "nav_hang_cancel: no RESULT_CANCELED in nav log"
    fi
    ;;
  pick_hang_cancel)
    [[ "${BACKEND}" == "ros" ]] || fail "pick_hang_cancel requires BACKEND=ros"

    publish_event "intercept_reached"
    sleep 1
    read_status "after_intercept_reached"

    state_after_pick_trigger="$(status_field "state" "${LAST_STATUS_JSON}")"
    summary_after_pick_trigger="$(status_field "chosen_transition_summary" "${LAST_STATUS_JSON}")"
    dispatched_after_pick_trigger="$(status_field "last_dispatched_actions_count" "${LAST_STATUS_JSON}")"
    [[ "${state_after_pick_trigger}" == "PICK" ]] || fail "pick_hang_cancel: expected state PICK after intercept_reached, got ${state_after_pick_trigger}"
    [[ "${summary_after_pick_trigger}" == *"--intercept_reached--> PICK" ]] || fail "pick_hang_cancel: unexpected transition summary '${summary_after_pick_trigger}'"
    [[ "${dispatched_after_pick_trigger}" -gt 0 ]] || fail "pick_hang_cancel: expected dispatched actions > 0 after intercept_reached"

    wait_for_log "pick goal received" "${MANIP_LOG}" 20 || fail "pick_hang_cancel: no pick goal received in manipulation log"

    publish_event "vc_abort"
    sleep 1
    read_status "after_vc_abort"

    state_after_abort="$(status_field "state" "${LAST_STATUS_JSON}")"
    event_after_abort="$(status_field "last_event" "${LAST_STATUS_JSON}")"
    [[ "${state_after_abort}" == "IDLE" ]] || fail "pick_hang_cancel: expected state IDLE after vc_abort, got ${state_after_abort}"
    [[ "${event_after_abort}" == "vc_abort" ]] || fail "pick_hang_cancel: expected last_event vc_abort, got ${event_after_abort}"

    manual_reset="$(status_list_contains "applied_context_updates" "manual_override_active := False" "${LAST_STATUS_JSON}")"
    knav_reset="$(status_list_contains "applied_context_updates" "k_nav := 0" "${LAST_STATUS_JSON}")"
    pick_retry_reset="$(status_list_contains "applied_context_updates" "pick_retries := 0" "${LAST_STATUS_JSON}")"
    [[ "${manual_reset}" == "1" ]] || fail "pick_hang_cancel: vc_abort status missing manual_override_active reset"
    [[ "${knav_reset}" == "1" ]] || fail "pick_hang_cancel: vc_abort status missing k_nav reset"
    [[ "${pick_retry_reset}" == "1" ]] || fail "pick_hang_cancel: vc_abort status missing pick_retries reset"

    wait_for_log "pick cancel received" "${MANIP_LOG}" 20 || fail "pick_hang_cancel: no pick cancel received in manipulation log"
    wait_for_log "pick result=canceled" "${MANIP_LOG}" 20 || fail "pick_hang_cancel: no pick canceled result in manipulation log"
    ;;
  real_nav2_goal_send)
    [[ "${BACKEND}" == "real_nav2" || "${BACKEND}" == "real" ]] || fail "real_nav2_goal_send requires BACKEND=real_nav2"
    pose_provided="$(status_field "last_nav_goal_pose_provided" "${LAST_STATUS_JSON}")"
    [[ "${pose_provided}" == "True" || "${pose_provided}" == "true" ]] || fail "real_nav2_goal_send: expected last_nav_goal_pose_provided=true"
    wait_for_log "GOAL_RECEIVED" "${NAV_LOG}" 20 || fail "real_nav2_goal_send: no GOAL_RECEIVED in nav log"
    ;;
  real_nav2_cancel)
    [[ "${BACKEND}" == "real_nav2" || "${BACKEND}" == "real" ]] || fail "real_nav2_cancel requires BACKEND=real_nav2"
    wait_for_log "GOAL_RECEIVED" "${NAV_LOG}" 20 || fail "real_nav2_cancel: no GOAL_RECEIVED in nav log"
    publish_event "vc_abort"
    sleep 1
    read_status "after_vc_abort"
    state_after_abort="$(status_field "state" "${LAST_STATUS_JSON}")"
    [[ "${state_after_abort}" == "IDLE" ]] || fail "real_nav2_cancel: expected state IDLE, got ${state_after_abort}"
    wait_for_log "CANCEL_RECEIVED" "${NAV_LOG}" 20 || fail "real_nav2_cancel: no CANCEL_RECEIVED in nav log"
    wait_for_log "RESULT_CANCELED" "${NAV_LOG}" 20 || fail "real_nav2_cancel: no RESULT_CANCELED in nav log"
    ;;
  real_nav2_auto_result_success)
    [[ "${BACKEND}" == "real_nav2" || "${BACKEND}" == "real" ]] || fail "real_nav2_auto_result_success requires BACKEND=real_nav2"
    wait_for_log "GOAL_RECEIVED" "${NAV_LOG}" 20 || fail "real_nav2_auto_result_success: no GOAL_RECEIVED in nav log"
    wait_for_log "RESULT_SUCCEEDED" "${NAV_LOG}" 20 || fail "real_nav2_auto_result_success: no RESULT_SUCCEEDED in nav log"
    wait_for_state "OBSERVE_HAND" 20 "auto_result_success" || fail "real_nav2_auto_result_success: expected state OBSERVE_HAND after auto result bridge"
    summary_after_result="$(status_field "chosen_transition_summary" "${LAST_STATUS_JSON}")"
    event_after_result="$(status_field "last_event" "${LAST_STATUS_JSON}")"
    [[ "${event_after_result}" == "approach_reached" ]] || fail "real_nav2_auto_result_success: expected last_event approach_reached, got ${event_after_result}"
    [[ "${summary_after_result}" == *"--approach_reached--> OBSERVE_HAND" ]] || fail "real_nav2_auto_result_success: unexpected transition summary '${summary_after_result}'"
    ;;
  real_nav2_auto_result_fail)
    [[ "${BACKEND}" == "real_nav2" || "${BACKEND}" == "real" ]] || fail "real_nav2_auto_result_fail requires BACKEND=real_nav2"
    wait_for_log "GOAL_RECEIVED" "${NAV_LOG}" 20 || fail "real_nav2_auto_result_fail: no GOAL_RECEIVED in nav log"
    wait_for_log "RESULT_ABORTED" "${NAV_LOG}" 20 || fail "real_nav2_auto_result_fail: no RESULT_ABORTED in nav log"
    wait_for_state "SEARCH_PERSON" 20 "auto_result_fail" || fail "real_nav2_auto_result_fail: expected state SEARCH_PERSON after auto fail bridge"
    summary_after_result="$(status_field "chosen_transition_summary" "${LAST_STATUS_JSON}")"
    event_after_result="$(status_field "last_event" "${LAST_STATUS_JSON}")"
    [[ "${event_after_result}" == "nav_failed" ]] || fail "real_nav2_auto_result_fail: expected last_event nav_failed, got ${event_after_result}"
    [[ "${summary_after_result}" == *"--nav_failed--> SEARCH_PERSON" ]] || fail "real_nav2_auto_result_fail: unexpected transition summary '${summary_after_result}'"
    ;;
esac

echo "[demo] PASS case=${DEMO_CASE}"
echo "[demo] logs: ${LOG_DIR}"
