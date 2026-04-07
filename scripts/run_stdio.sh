#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
ENV_FILE="${ROOT_DIR}/.env"

if [[ -t 0 && -t 1 ]]; then
  cat >&2 <<EOF
This script starts an MCP stdio server.
It is meant to be launched by an MCP client, not used directly in an interactive shell.

What to do instead:
1. Configure your MCP client to run:
   ${ROOT_DIR}/scripts/run_stdio.sh
2. Or run it non-interactively from a client/inspector.

If you start a stdio MCP server in a normal terminal and press Enter,
the server receives a blank line instead of a JSON-RPC message and logs
errors like "Invalid JSON: EOF while parsing a value".
EOF
  exit 1
fi

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
