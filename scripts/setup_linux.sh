#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"

find_python() {
  local candidate
  for candidate in python3.12 python3.11 python3.10; do
    if command -v "${candidate}" >/dev/null 2>&1; then
      echo "${candidate}"
      return 0
    fi
  done
  return 1
}

PYTHON_BIN="${PYTHON_BIN:-}"
if [[ -z "${PYTHON_BIN}" ]]; then
  if ! PYTHON_BIN="$(find_python)"; then
    echo "Python 3.10+ is required. Install python3.10, python3.11, or python3.12 first." >&2
    exit 1
  fi
fi

echo "Using Python: ${PYTHON_BIN}"
"${PYTHON_BIN}" -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip
python -m pip install -e "${ROOT_DIR}"

echo
echo "Setup complete."
echo "Next:"
echo "  export AIR_KOREA_SERVICE_KEY='your-service-key'"
echo "  ${ROOT_DIR}/scripts/run_stdio.sh"
