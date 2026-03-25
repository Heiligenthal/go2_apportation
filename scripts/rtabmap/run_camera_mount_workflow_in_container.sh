#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNTIME_WRAPPER="${ROOT_DIR}/scripts/bringup/run_board_runtime.sh"
INNER_WORKFLOW="./scripts/rtabmap/camera_mount_workflow.sh"

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/rtabmap/run_camera_mount_workflow_in_container.sh <subcommand> [args...]

Supported subcommands:
  record
  dry-run
  calibrate
  reference-map

Examples:
  ./scripts/rtabmap/run_camera_mount_workflow_in_container.sh record
  ./scripts/rtabmap/run_camera_mount_workflow_in_container.sh record --with-scan
  ./scripts/rtabmap/run_camera_mount_workflow_in_container.sh dry-run --bootstrap-seconds 10
  ./scripts/rtabmap/run_camera_mount_workflow_in_container.sh calibrate --fast-trials 40 --refine-trials 10
  ./scripts/rtabmap/run_camera_mount_workflow_in_container.sh reference-map
USAGE
}

log() {
  printf '[run_camera_mount_workflow_in_container] %s\n' "$*"
}

die() {
  printf '[run_camera_mount_workflow_in_container] ERROR: %s\n' "$*" >&2
  exit 1
}

build_inner_command() {
  local cmd
  cmd="cd /workspace/repo && ${INNER_WORKFLOW}"
  for arg in "$@"; do
    printf -v cmd '%s %q' "$cmd" "$arg"
  done
  printf '%s\n' "$cmd"
}

main() {
  local subcommand inner_command
  subcommand="${1:-}"

  case "${subcommand}" in
    record|dry-run|calibrate|reference-map)
      ;;
    help|-h|--help|"")
      usage
      exit 0
      ;;
    *)
      die "Unsupported subcommand '${subcommand}'. Supported: record, dry-run, calibrate, reference-map"
      ;;
  esac

  [[ -x "${RUNTIME_WRAPPER}" ]] || die "Runtime wrapper not found or not executable: ${RUNTIME_WRAPPER}"

  inner_command="$(build_inner_command "$@")"

  log "Using canonical runtime container entry: ${RUNTIME_WRAPPER}"
  log "Executing inside container: ${INNER_WORKFLOW} $*"

  "${RUNTIME_WRAPPER}" --run "${inner_command}"
}

main "$@"
