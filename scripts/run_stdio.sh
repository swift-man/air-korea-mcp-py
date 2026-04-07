#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
ENV_FILE="${ROOT_DIR}/.env"

if [[ ! -f "${VENV_DIR}/bin/activate" ]]; then
  echo "Virtual environment not found. Run ${ROOT_DIR}/scripts/setup_linux.sh first." >&2
  exit 1
fi

source "${VENV_DIR}/bin/activate"

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
fi

if [[ -z "${AIR_KOREA_SERVICE_KEY:-}" && -z "${AIR_KOREA_SERVICE_KEY_ENCODED:-}" ]]; then
  echo "Set AIR_KOREA_SERVICE_KEY or AIR_KOREA_SERVICE_KEY_ENCODED before running." >&2
  exit 1
fi

exec air-korea-mcp
