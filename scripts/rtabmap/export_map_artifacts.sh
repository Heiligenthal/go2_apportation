#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTAINER_NAME="${CONTAINER_NAME:-go2_board_runtime}"
MAP_DIR=""
DB_PATH=""
WITH_CLOUD=0
REUSE_CONTAINER=1
RESTART_CONTAINER=0

usage() {
  cat <<'USAGE'
Usage:
  scripts/rtabmap/export_map_artifacts.sh [options]

Options:
  --map-dir <path>        Map directory (default: latest artifacts/maps/<timestamp>)
  --db <path>             Explicit DB path (default: <map-dir>/rtabmap.db)
  --with-cloud            Export cloud.ply in addition to map.pgm/map.yaml
  --reuse-container       Reuse running go2_board_runtime container (default)
  --restart-container     Stop running container and start a new one
  -h, --help              Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --map-dir)
      [[ $# -lt 2 ]] && { echo "[export_map_artifacts] ERROR: --map-dir requires a value." >&2; exit 2; }
      MAP_DIR="$2"
      shift 2
      ;;
    --db)
      [[ $# -lt 2 ]] && { echo "[export_map_artifacts] ERROR: --db requires a value." >&2; exit 2; }
      DB_PATH="$2"
      shift 2
      ;;
    --with-cloud)
      WITH_CLOUD=1
      shift
      ;;
    --reuse-container)
      REUSE_CONTAINER=1
      RESTART_CONTAINER=0
      shift
      ;;
    --restart-container)
      RESTART_CONTAINER=1
      REUSE_CONTAINER=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[export_map_artifacts] ERROR: unknown argument '$1'." >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "[export_map_artifacts] ERROR: docker CLI not found." >&2
  exit 1
fi

if [[ ! -x "${ROOT_DIR}/scripts/bringup/run_board_runtime.sh" ]]; then
  echo "[export_map_artifacts] ERROR: scripts/bringup/run_board_runtime.sh missing or not executable." >&2
  exit 1
fi

if [[ -z "${MAP_DIR}" ]]; then
  latest_map_dir="$(ls -1dt "${ROOT_DIR}"/artifacts/maps/* 2>/dev/null | head -n 1 || true)"
  if [[ -z "${latest_map_dir}" ]]; then
    echo "[export_map_artifacts] ERROR: no artifacts/maps/<timestamp>/ directory found. Use --map-dir." >&2
    exit 1
  fi
  MAP_DIR="${latest_map_dir}"
fi

if [[ "${MAP_DIR}" != /* ]]; then
  MAP_DIR="${ROOT_DIR}/${MAP_DIR}"
fi

if [[ ! -d "${MAP_DIR}" ]]; then
  echo "[export_map_artifacts] ERROR: map directory not found: ${MAP_DIR}" >&2
  exit 1
fi

if [[ -z "${DB_PATH}" ]]; then
  DB_PATH="${MAP_DIR}/rtabmap.db"
fi

if [[ "${DB_PATH}" != /* ]]; then
  DB_PATH="${ROOT_DIR}/${DB_PATH}"
fi

if [[ ! -f "${DB_PATH}" ]]; then
  echo "[export_map_artifacts] ERROR: database not found: ${DB_PATH}" >&2
  exit 1
fi

DB_SANITY_LOG="${MAP_DIR}/export.db_sanity.log"
if ! python3 "${ROOT_DIR}/scripts/rtabmap/check_rtabmap_db_sanity.py" \
  --db "${DB_PATH}" \
  --context "export_map_artifacts" \
  --artifact-dir "${MAP_DIR}" \
  --log-path "${DB_SANITY_LOG}" \
  >"${DB_SANITY_LOG}" 2>&1; then
  echo "[export_map_artifacts] ERROR: RTAB-Map DB sanity check failed for ${DB_PATH}" >&2
  echo "[export_map_artifacts] See ${DB_SANITY_LOG}" >&2
  exit 1
fi

if [[ "${DB_PATH}" != "${ROOT_DIR}"/* || "${MAP_DIR}" != "${ROOT_DIR}"/* ]]; then
  echo "[export_map_artifacts] ERROR: paths must be under repo root (${ROOT_DIR}) so container mapping works." >&2
  exit 1
fi

container_running() {
  docker ps --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"
}

if container_running; then
  if [[ "${RESTART_CONTAINER}" -eq 1 ]]; then
    echo "[export_map_artifacts] Stopping running container '${CONTAINER_NAME}' (--restart-container)."
    docker stop "${CONTAINER_NAME}" >/dev/null
  elif [[ "${REUSE_CONTAINER}" -eq 1 ]]; then
    echo "[export_map_artifacts] Reusing running container '${CONTAINER_NAME}'."
  fi
fi

if ! container_running; then
  echo "[export_map_artifacts] Starting runtime container '${CONTAINER_NAME}' via run_board_runtime.sh --run 'sleep infinity'."
  CONTAINER_NAME="${CONTAINER_NAME}" "${ROOT_DIR}/scripts/bringup/run_board_runtime.sh" --run "sleep infinity" \
    >"${MAP_DIR}/export.container_start.stdout.log" \
    2>"${MAP_DIR}/export.container_start.stderr.log" &
  launcher_pid=$!

  ready=0
  for _ in $(seq 1 30); do
    if container_running; then
      ready=1
      break
    fi
    if ! kill -0 "${launcher_pid}" 2>/dev/null; then
      break
    fi
    sleep 1
  done

  if [[ "${ready}" -ne 1 ]]; then
    echo "[export_map_artifacts] ERROR: container '${CONTAINER_NAME}' did not become ready." >&2
    echo "[export_map_artifacts] See ${MAP_DIR}/export.container_start.stderr.log" >&2
    exit 1
  fi
fi

MAP_DIR_CONT="/workspace/repo${MAP_DIR#${ROOT_DIR}}"
DB_PATH_CONT="/workspace/repo${DB_PATH#${ROOT_DIR}}"
EXPORT_STDOUT="${MAP_DIR}/export.stdout.log"
EXPORT_STDERR="${MAP_DIR}/export.stderr.log"

set +e
docker exec \
  -e MAP_DIR_CONT="${MAP_DIR_CONT}" \
  -e DB_PATH_CONT="${DB_PATH_CONT}" \
  -e WITH_CLOUD="${WITH_CLOUD}" \
  "${CONTAINER_NAME}" \
  bash -lc '
set -euo pipefail
source /opt/ros/humble/setup.bash

if ! command -v rtabmap-reprocess >/dev/null 2>&1; then
  echo "Missing required tool: rtabmap-reprocess. Rebuild runtime image with RTAB-Map packages." >&2
  exit 10
fi

if [[ "${WITH_CLOUD}" -eq 1 ]] && ! command -v rtabmap-export >/dev/null 2>&1; then
  echo "Missing required tool: rtabmap-export for --with-cloud." >&2
  exit 11
fi

TMP_DB="${MAP_DIR_CONT}/_reprocess_export.db"
TMP_PGM="${MAP_DIR_CONT}/_reprocess_export_map.pgm"
PARAMS_DUMP="${MAP_DIR_CONT}/_db_params.ini"

rm -f "${TMP_DB}" "${TMP_PGM}" "${PARAMS_DUMP}"

# 2D occupancy export from DB
rtabmap-reprocess -g2 "${DB_PATH_CONT}" "${TMP_DB}"

if [[ ! -f "${TMP_PGM}" ]]; then
  echo "Expected map image was not generated: ${TMP_PGM}" >&2
  exit 12
fi

mv -f "${TMP_PGM}" "${MAP_DIR_CONT}/map.pgm"

if ! command -v rtabmap-info >/dev/null 2>&1; then
  echo "Missing required tool: rtabmap-info (needed to derive map.yaml resolution)." >&2
  exit 13
fi

if ! rtabmap-info --dump "${PARAMS_DUMP}" "${DB_PATH_CONT}" >/dev/null 2>&1; then
  echo "Failed to dump DB parameters with rtabmap-info for YAML generation." >&2
  exit 14
fi

resolution="$(awk -F= '$1=="Grid/CellSize" {print $2}' "${PARAMS_DUMP}" | tail -n 1)"
if [[ -z "${resolution}" ]]; then
  echo "Could not determine Grid/CellSize from DB parameters. Cannot generate map.yaml safely." >&2
  exit 15
fi

cat > "${MAP_DIR_CONT}/map.yaml" <<YAML
image: map.pgm
resolution: ${resolution}
origin: [0.0, 0.0, 0.0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.196
YAML

if [[ "${WITH_CLOUD}" -eq 1 ]]; then
  rtabmap-export --cloud --output cloud --output_dir "${MAP_DIR_CONT}" "${DB_PATH_CONT}"
  if [[ ! -f "${MAP_DIR_CONT}/cloud.ply" ]]; then
    echo "cloud.ply was requested but not generated." >&2
    exit 16
  fi
fi

rm -f "${TMP_DB}" "${PARAMS_DUMP}"
' >"${EXPORT_STDOUT}" 2>"${EXPORT_STDERR}"
RC=$?
set -e

if [[ ${RC} -ne 0 ]]; then
  echo "[export_map_artifacts] FAIL: export command failed (rc=${RC})." >&2
  echo "[export_map_artifacts] See ${EXPORT_STDOUT} and ${EXPORT_STDERR}" >&2
  exit "${RC}"
fi

echo "[export_map_artifacts] PASS"
echo "[export_map_artifacts] map dir: ${MAP_DIR}"
echo "[export_map_artifacts] exported: map.pgm map.yaml$([[ "${WITH_CLOUD}" -eq 1 ]] && echo ' cloud.ply')"
