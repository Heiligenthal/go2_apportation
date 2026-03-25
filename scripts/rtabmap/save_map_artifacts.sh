#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOPICS_FILE="${TOPICS_FILE:-${ROOT_DIR}/config/runtime_topics.yaml}"
ARTIFACT_ROOT="${ROOT_DIR}/artifacts/rtabmap"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${ARTIFACT_ROOT}/${TIMESTAMP}"

mkdir -p "${RUN_DIR}"

default_db_path="${HOME}/.ros/rtabmap.db"
database_path="${default_db_path}"

if [[ -f "${TOPICS_FILE}" ]]; then
  extracted_db="$(awk -F': *' '$1 ~ "^[[:space:]]*database_path$" {print $2}' "${TOPICS_FILE}" | tr -d '"' | tail -n 1)"
  if [[ -n "${extracted_db}" && "${extracted_db}" != "<"*">" ]]; then
    database_path="${extracted_db}"
  fi
fi

if [[ -f "${database_path}" ]]; then
  cp -a "${database_path}" "${RUN_DIR}/rtabmap.db"
  echo "[save_map_artifacts] Saved database: ${RUN_DIR}/rtabmap.db"
else
  echo "[save_map_artifacts] WARN: database not found at ${database_path}" >&2
fi

if [[ -f "${TOPICS_FILE}" ]]; then
  cp -a "${TOPICS_FILE}" "${RUN_DIR}/runtime_topics.yaml"
fi

echo "[save_map_artifacts] Artifacts directory: ${RUN_DIR}"
