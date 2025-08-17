#!/usr/bin/env bash
set -euo pipefail

# Start the LAN Modder FastAPI app
REPO_ROOT="/home/tdeshane/luanti"
APP_DIR="$REPO_ROOT/lan_modder"
VENV_DIR="$APP_DIR/.venv"

if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
  source "$VENV_DIR/bin/activate"
  pip install -U pip wheel
  pip install -r "$APP_DIR/requirements.txt"
else
  source "$VENV_DIR/bin/activate"
  pip install -r "$APP_DIR/requirements.txt" --upgrade --quiet || true
fi

export HOST=0.0.0.0
export PORT=8088
# Ensure the app talks to the user ollama daemon
export OLLAMA_HOST="http://127.0.0.1:11434"

# Ensure Ollama models are present (best-effort)
if command -v ollama >/dev/null 2>&1; then
  # Pull as the invoking user, not root, so models land in the user's store
  if [[ -n "${SUDO_USER:-}" ]]; then
    (sudo -u "$SUDO_USER" -H env OLLAMA_HOST="$OLLAMA_HOST" ollama pull gpt-oss:20b || true) &
    (sudo -u "$SUDO_USER" -H env OLLAMA_HOST="$OLLAMA_HOST" ollama pull gpt-oss:120b || true) &
  else
    (env OLLAMA_HOST="$OLLAMA_HOST" ollama pull gpt-oss:20b || true) &
    (env OLLAMA_HOST="$OLLAMA_HOST" ollama pull gpt-oss:120b || true) &
  fi
fi

cd "$REPO_ROOT"
python -m uvicorn lan_modder.app:app --host "$HOST" --port "$PORT"
