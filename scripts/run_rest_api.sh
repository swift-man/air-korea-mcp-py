#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
ENV_FILE="${ROOT_DIR}/.env"

if [[ ! -f "${VENV_DIR}/bin/activate" ]]; then
  echo "Virtual environment not found. Create .venv and install the project first." >&2
  exit 1
fi

source "${VENV_DIR}/bin/activate"

if [[ -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

if [[ -z "${AIR_KOREA_SERVICE_KEY:-}" && -z "${AIR_KOREA_SERVICE_KEY_ENCODED:-}" ]]; then
  echo "Set AIR_KOREA_SERVICE_KEY or AIR_KOREA_SERVICE_KEY_ENCODED before running." >&2
  exit 1
fi

export AIR_KOREA_REST_HOST="${AIR_KOREA_REST_HOST:-127.0.0.1}"
export AIR_KOREA_REST_PORT="${AIR_KOREA_REST_PORT:-8010}"

echo "Starting Air Korea REST API"
echo "Endpoint: http://${AIR_KOREA_REST_HOST}:${AIR_KOREA_REST_PORT}"

exec air-korea-rest-api
