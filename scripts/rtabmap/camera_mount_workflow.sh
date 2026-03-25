#!/usr/bin/env bash
set -eo pipefail

REALSENSE_PID=""
BOARD_PID=""
RECORD_PID=""
RECORD_RUNTIME_DIR=""
WAIT_FAILURE_REASON=""
WAIT_MISSING_TOPICS=()

usage() {
  cat <<'USAGE'
Usage:
  ./camera_mount_workflow.sh record [--with-scan]
  ./camera_mount_workflow.sh dry-run [--bootstrap-seconds N] [--fast-trials N] [--refine-trials N] [--use-scan-score]
  ./camera_mount_workflow.sh calibrate [--bootstrap-seconds N] [--fast-trials N] [--refine-trials N] [--use-scan-score]
  ./camera_mount_workflow.sh reference-map [--with-scan] [--output-tag TAG]
  ./camera_mount_workflow.sh latest-bag
  ./camera_mount_workflow.sh check
  ./camera_mount_workflow.sh help

What it does:
  - finds the repo root automatically
  - sources ROS and workspace setup files automatically
  - records a calibration bag with the required camera topics
  - checks the newest bag for required camera topics
  - starts the camera mount calibration script with sensible defaults
  - runs a final replay mapping pass from the best calibration result

Defaults:
  bootstrap-seconds = 10
  fast-trials       = 40
  refine-trials     = 10

Examples:
  ./camera_mount_workflow.sh record
  ./camera_mount_workflow.sh record --with-scan
  ./camera_mount_workflow.sh dry-run
  ./camera_mount_workflow.sh calibrate --use-scan-score
  ./camera_mount_workflow.sh reference-map
USAGE
}

log() {
  printf '[camera-mount-workflow] %s\n' "$*"
}

die() {
  printf '[camera-mount-workflow] ERROR: %s\n' "$*" >&2
  exit 1
}

source_bash_file() {
  local file_path rc
  file_path="$1"

  set +e
  # shellcheck disable=SC1090
  source "$file_path"
  rc=$?
  set -e

  return "$rc"
}

find_repo_root() {
  local start_dir script_dir current
  script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

  for start_dir in "$PWD" "$script_dir"; do
    current="$start_dir"
    while [[ "$current" != "/" ]]; do
      if [[ -d "$current/scripts/rtabmap" && -d "$current/artifacts" ]]; then
        printf '%s\n' "$current"
        return 0
      fi
      current="$(dirname -- "$current")"
    done
  done

  die "Repo root not found. Put this script inside the repo or run it from the repo root."
}

source_ros_env() {
  local repo_root ros_setup ws_container_setup ws_setup ws_local_setup runtime_context
  repo_root="$1"

  set +u
  if [[ -f "/.dockerenv" ]]; then
    runtime_context="inside a container"
  else
    runtime_context="outside the container"
  fi
  log "Detected repo root: $repo_root"
  log "Runtime context: $runtime_context"

  ros_setup="/opt/ros/humble/setup.bash"
  [[ -f "$ros_setup" ]] || die "ROS 2 Humble setup not found at $ros_setup. Run this script inside the intended Board-Runtime Docker container."
  source_bash_file "$ros_setup" || die "Failed to source ROS 2 Humble setup: $ros_setup"
  log "Sourced $ros_setup"

  ws_container_setup="$repo_root/install_container/setup.bash"
  ws_setup="$repo_root/install/setup.bash"
  ws_local_setup="$repo_root/install/local_setup.bash"

  if [[ -f "$ws_container_setup" ]]; then
    if source_bash_file "$ws_container_setup"; then
      log "Sourced $ws_container_setup"
      set -u
      return
    fi
    log "Sourcing $ws_container_setup failed."
  fi

  if [[ -f "$ws_setup" ]]; then
    if source_bash_file "$ws_setup"; then
      log "Sourced $ws_setup"
      set -u
      return
    fi
    log "Sourcing $ws_setup failed."
  fi

  if [[ -f "$ws_local_setup" ]]; then
    if source_bash_file "$ws_local_setup"; then
      log "Sourced $ws_local_setup as local workspace overlay fallback"
      set -u
      return
    fi
    log "Sourcing $ws_local_setup failed."
  fi

  die "No workspace overlay could be sourced. Tried: $ws_container_setup, $ws_setup, $ws_local_setup"

  set -u
}

ensure_tools() {
  command -v ros2 >/dev/null 2>&1 || die "ros2 not found in PATH after sourcing environment."
  command -v python3 >/dev/null 2>&1 || die "python3 not found in PATH."
}

start_process_bg() {
  local name out_log err_log
  name="$1"
  out_log="$2"
  err_log="$3"
  shift 3 || true

  set +e
  "$@" >"$out_log" 2>"$err_log" &
  local pid=$!
  set -e

  printf '[camera-mount-workflow] Started %s (pid=%s)\n' "$name" "$pid" >&2
  printf '%s\n' "$pid"
}

stop_pid() {
  local pid name
  pid="$1"
  name="$2"

  [[ -n "$pid" ]] || return 0
  if ! kill -0 "$pid" 2>/dev/null; then
    return 0
  fi

  kill -INT "$pid" >/dev/null 2>&1 || true
  for _ in $(seq 1 8); do
    if ! kill -0 "$pid" 2>/dev/null; then
      wait "$pid" >/dev/null 2>&1 || true
      log "Stopped ${name} (pid=${pid})"
      return 0
    fi
    sleep 1
  done

  kill -TERM "$pid" >/dev/null 2>&1 || true
  wait "$pid" >/dev/null 2>&1 || true
  log "Stopped ${name} (pid=${pid})"
}

cleanup_record_processes() {
  set +e
  stop_pid "$RECORD_PID" "ros2 bag record"
  stop_pid "$BOARD_PID" "board_description"
  stop_pid "$REALSENSE_PID" "realsense"
}

topic_visible() {
  local topic
  topic="$1"
  ros2 topic list 2>/dev/null | grep -Fxq "$topic"
}

wait_for_topics() {
  local timeout_seconds
  timeout_seconds="$1"
  shift || true

  local deadline missing_topics topic
  WAIT_FAILURE_REASON=""
  WAIT_MISSING_TOPICS=()
  deadline=$((SECONDS + timeout_seconds))
  while ((SECONDS < deadline)); do
    missing_topics=()

    if [[ -n "$REALSENSE_PID" ]] && ! kill -0 "$REALSENSE_PID" 2>/dev/null; then
      WAIT_FAILURE_REASON="RealSense producer exited before all required topics became available. See ${RECORD_RUNTIME_DIR}/realsense.err.log"
      return 1
    fi
    if [[ -n "$BOARD_PID" ]] && ! kill -0 "$BOARD_PID" 2>/dev/null; then
      WAIT_FAILURE_REASON="board_description producer exited before all required topics became available. See ${RECORD_RUNTIME_DIR}/board_description.err.log"
      return 1
    fi

    for topic in "$@"; do
      if ! topic_visible "$topic"; then
        missing_topics+=("$topic")
      fi
    done

    if ((${#missing_topics[@]} == 0)); then
      return 0
    fi

    sleep 1
  done

  WAIT_MISSING_TOPICS=("${missing_topics[@]}")
  WAIT_FAILURE_REASON="Required topics did not become available within timeout."
  return 1
}

record_cmd() {
  local repo_root with_scan=0 arg bag_parent bag_dir record_stamp
  repo_root="$1"
  shift || true

  while (($#)); do
    arg="$1"
    case "$arg" in
      --with-scan)
        with_scan=1
        ;;
      -h|--help|help)
        usage
        exit 0
        ;;
      *)
        die "Unknown option for record: $arg"
        ;;
    esac
    shift || true
  done

  bag_parent="$repo_root/artifacts/bags"
  mkdir -p "$bag_parent"
  bag_dir="$bag_parent/calibration_$(date +%Y%m%d_%H%M%S)"
  record_stamp="${bag_dir##*/calibration_}"
  RECORD_RUNTIME_DIR="$repo_root/artifacts/bags/.record_runtime_${record_stamp}"
  mkdir -p "$RECORD_RUNTIME_DIR"

  local -a topics=(
    "/camera/realsense2_camera/color/image_raw"
    "/camera/realsense2_camera/aligned_depth_to_color/image_raw"
    "/camera/realsense2_camera/color/camera_info"
    "/utlidar/robot_odom"
    "/tf"
    "/tf_static"
  )

  if [[ "$with_scan" -eq 1 ]]; then
    topics+=("/scan")
  fi

  local -a required_topics=(
    "/camera/realsense2_camera/color/image_raw"
    "/camera/realsense2_camera/aligned_depth_to_color/image_raw"
    "/camera/realsense2_camera/color/camera_info"
    "/utlidar/robot_odom"
  )

  local -a optional_topics=(
    "/tf"
    "/tf_static"
  )

  trap cleanup_record_processes EXIT INT TERM

  log "Starting required producers before recording"
  log "Producer launch style follows the existing repo pattern: ros2 launch launch/realsense_board.launch.py and ros2 launch launch/board_description.launch.py"
  REALSENSE_PID="$(start_process_bg \
    "realsense" \
    "$RECORD_RUNTIME_DIR/realsense.out.log" \
    "$RECORD_RUNTIME_DIR/realsense.err.log" \
    ros2 launch launch/realsense_board.launch.py)"
  BOARD_PID="$(start_process_bg \
    "board_description" \
    "$RECORD_RUNTIME_DIR/board_description.out.log" \
    "$RECORD_RUNTIME_DIR/board_description.err.log" \
    ros2 launch launch/board_description.launch.py)"

  log "Waiting for required topics:"
  printf '  %s\n' "${required_topics[@]}"
  if ! wait_for_topics 60 "${required_topics[@]}"; then
    if [[ -n "$WAIT_FAILURE_REASON" && "$WAIT_FAILURE_REASON" != "Required topics did not become available within timeout." ]]; then
      die "$WAIT_FAILURE_REASON"
    fi
    die "${WAIT_FAILURE_REASON} Missing: ${WAIT_MISSING_TOPICS[*]}"
  fi

  log "All required topics are available."
  log "Optional topic check:"
  for arg in "${optional_topics[@]}"; do
    if topic_visible "$arg"; then
      log "  available: $arg"
    else
      log "  not yet visible: $arg"
    fi
  done

  log "Recording calibration bag"
  log "Started producers:"
  log "  realsense -> $REALSENSE_PID"
  log "  board_description -> $BOARD_PID"
  log "Output directory will be: $bag_dir"
  log "Topics:"
  printf '  %s\n' "${topics[@]}"
  log "Stop recording with Ctrl+C"

  ros2 bag record -o "$bag_dir" "${topics[@]}" &
  RECORD_PID=$!
  wait "$RECORD_PID"
  RECORD_PID=""
}

latest_bag_path() {
  local repo_root bag
  repo_root="$1"
  find "$repo_root/artifacts/bags" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' 2>/dev/null \
    | sort -nr \
    | awk '{print $2}' \
    | while IFS= read -r bag; do
        [[ -f "$bag/metadata.yaml" ]] || continue
        printf '%s\n' "$bag"
        break
      done
}

bag_has_required_camera_topics() {
  local bag info
  bag="$1"
  info="$(ros2 bag info "$bag" 2>&1 || true)"
  grep -q '/camera/realsense2_camera/color/image_raw' <<<"$info" \
    && grep -q '/camera/realsense2_camera/aligned_depth_to_color/image_raw' <<<"$info" \
    && grep -q '/camera/realsense2_camera/color/camera_info' <<<"$info"
}

check_cmd() {
  local repo_root bag
  repo_root="$1"
  bag="$(latest_bag_path "$repo_root")"
  [[ -n "$bag" ]] || die "No valid bag with metadata.yaml found under $repo_root/artifacts/bags"

  log "Newest valid bag: $bag"
  ros2 bag info "$bag"

  if bag_has_required_camera_topics "$bag"; then
    log "Newest bag contains required camera topics."
  else
    die "Newest valid bag does not contain the required camera topics for camera-mount calibration. Record a new bag first."
  fi
}

run_calibration_cmd() {
  local repo_root mode bootstrap_seconds=10 fast_trials=40 refine_trials=10 use_scan_score=0 arg bag calib_script ensure_env_script pydeps_dir pydeps_pythonpath
  repo_root="$1"
  mode="$2"
  shift 2 || true

  while (($#)); do
    arg="$1"
    case "$arg" in
      --bootstrap-seconds)
        shift || die "Missing value after --bootstrap-seconds"
        bootstrap_seconds="$1"
        ;;
      --fast-trials)
        shift || die "Missing value after --fast-trials"
        fast_trials="$1"
        ;;
      --refine-trials)
        shift || die "Missing value after --refine-trials"
        refine_trials="$1"
        ;;
      --use-scan-score)
        use_scan_score=1
        ;;
      -h|--help|help)
        usage
        exit 0
        ;;
      *)
        die "Unknown option for $mode: $arg"
        ;;
    esac
    shift || true
  done

  bag="$(latest_bag_path "$repo_root")"
  [[ -n "$bag" ]] || die "No valid bag with metadata.yaml found under $repo_root/artifacts/bags"
  bag_has_required_camera_topics "$bag" || die "Newest valid bag is missing required camera topics. Record a new bag first."

  calib_script="$repo_root/scripts/rtabmap/calibrate_camera_mount_extrinsics.py"
  ensure_env_script="$repo_root/scripts/rtabmap/ensure_camera_mount_python_env.sh"
  pydeps_dir="$repo_root/.pydeps/camera_mount"
  pydeps_pythonpath="${pydeps_dir}${PYTHONPATH:+:${PYTHONPATH}}"
  [[ -f "$calib_script" ]] || die "Calibration script not found: $calib_script"
  [[ -x "$ensure_env_script" ]] || die "Python env helper not found or not executable: $ensure_env_script"

  "$ensure_env_script" --mode "$mode"
  [[ -d "$pydeps_dir" ]] || die "Camera-mount pydeps dir not found after setup: $pydeps_dir"

  log "Using newest valid bag: $bag"
  log "Calibration script: $calib_script"
  log "Using camera-mount pydeps dir: $pydeps_dir"
  log "Using python executable: $(command -v python3)"
  log "Using PYTHONPATH for calibration: $pydeps_pythonpath"
  log "bootstrap-seconds=$bootstrap_seconds fast-trials=$fast_trials refine-trials=$refine_trials use-scan-score=$use_scan_score"

  local -a cmd=(
    python3 "$calib_script"
    --bootstrap-seconds "$bootstrap_seconds"
    --fast-trials "$fast_trials"
    --refine-trials "$refine_trials"
  )

  if [[ "$mode" == "dry-run" ]]; then
    cmd+=(--dry-run)
  fi
  if [[ "$use_scan_score" -eq 1 ]]; then
    cmd+=(--use-scan-score)
  fi

  log "Executing: ${cmd[*]}"
  PYTHONPATH="$pydeps_pythonpath" "${cmd[@]}"
}

reference_map_cmd() {
  local repo_root replay_script arg with_scan=0 output_tag=""
  repo_root="$1"
  shift || true

  replay_script="$repo_root/scripts/rtabmap/run_reference_mapping_replay.sh"
  [[ -f "$replay_script" ]] || die "Replay mapping script not found: $replay_script"

  while (($#)); do
    arg="$1"
    case "$arg" in
      --with-scan)
        with_scan=1
        ;;
      --output-tag)
        shift || die "Missing value after --output-tag"
        output_tag="$1"
        ;;
      -h|--help|help)
        usage
        exit 0
        ;;
      *)
        die "Unknown option for reference-map: $arg"
        ;;
    esac
    shift || true
  done

  log "Running final replay mapping from the latest calibration result"
  log "Replay script: $replay_script"
  if [[ -n "$output_tag" ]]; then
    log "Using explicit output tag: $output_tag"
  fi

  local -a cmd=(bash "$replay_script")
  if [[ "$with_scan" -eq 1 ]]; then
    cmd+=(--with-scan)
  fi
  if [[ -n "$output_tag" ]]; then
    cmd+=(--output-tag "$output_tag")
  fi

  log "Executing: ${cmd[*]}"
  "${cmd[@]}"
}

main() {
  local subcommand repo_root
  subcommand="${1:-help}"
  if (($#)); then
    shift || true
  fi

  case "$subcommand" in
    help|-h|--help)
      usage
      exit 0
      ;;
  esac

  repo_root="$(find_repo_root)"
  source_ros_env "$repo_root"
  ensure_tools

  case "$subcommand" in
    record)
      record_cmd "$repo_root" "$@"
      ;;
    dry-run)
      run_calibration_cmd "$repo_root" "dry-run" "$@"
      ;;
    calibrate)
      run_calibration_cmd "$repo_root" "calibrate" "$@"
      ;;
    reference-map)
      reference_map_cmd "$repo_root" "$@"
      ;;
    latest-bag)
      latest_bag_path "$repo_root"
      ;;
    check)
      check_cmd "$repo_root"
      ;;
    *)
      die "Unknown subcommand: $subcommand"
      ;;
  esac
}

main "$@"
