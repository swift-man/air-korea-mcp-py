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
  # Auto-export variables defined in .env so the MCP process can read them.
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

if [[ -z "${AIR_KOREA_SERVICE_KEY:-}" && -z "${AIR_KOREA_SERVICE_KEY_ENCODED:-}" ]]; then
  echo "Set AIR_KOREA_SERVICE_KEY or AIR_KOREA_SERVICE_KEY_ENCODED before running." >&2
  exit 1
fi

export AIR_KOREA_MCP_HOST="${AIR_KOREA_MCP_HOST:-127.0.0.1}"
export AIR_KOREA_MCP_PORT="${AIR_KOREA_MCP_PORT:-8000}"
export AIR_KOREA_MCP_PATH="${AIR_KOREA_MCP_PATH:-/mcp}"

echo "Starting Air Korea MCP over streamable-http"
echo "Endpoint: http://${AIR_KOREA_MCP_HOST}:${AIR_KOREA_MCP_PORT}${AIR_KOREA_MCP_PATH}"

exec air-korea-mcp
