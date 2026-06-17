#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

export PORT="${PORT:-5001}"
export HOST="${HOST:-127.0.0.1}"
export LEON_TERMINAL_ACTIVITY="${LEON_TERMINAL_ACTIVITY:-1}"
export LEON_TERMINAL_LOG_LEVEL="${LEON_TERMINAL_LOG_LEVEL:-CRITICAL}"
export LEON_STARTUP_VERBOSE="${LEON_STARTUP_VERBOSE:-1}"

printf "\nLEON AI is starting...\n"

if [ ! -f "app.py" ]; then
  printf "app.py was not found. Please run start.sh from the LeonAI folder.\n" >&2
  exit 1
fi

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp .env.example .env
  printf "Created .env from .env.example. You can edit it later.\n"
fi

if [ -x "venv/bin/python" ]; then
  PYTHON="venv/bin/python"
else
  printf "Creating Python virtual environment...\n"
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv venv
  else
    python -m venv venv
  fi
  PYTHON="venv/bin/python"
fi

printf "Installing/checking Python packages...\n"
"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -r requirements.txt

if [ -f "scripts/leon_doctor.py" ]; then
  printf "Running release doctor...\n"
  "$PYTHON" scripts/leon_doctor.py
fi

printf "\nLEON AI is ready.\n"
printf "Open: http://127.0.0.1:%s\n\n" "$PORT"

"$PYTHON" app.py
