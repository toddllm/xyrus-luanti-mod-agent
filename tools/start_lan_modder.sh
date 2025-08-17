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

# Optional: pull models on start if explicitly requested
# Set OLLAMA_PULL_ON_START=true to enable (default: false)
if [[ "${OLLAMA_PULL_ON_START:-false}" == "true" ]] && command -v ollama >/dev/null 2>&1; then
  check_or_pull() {
    local model="$1"
    if [[ -n "${SUDO_USER:-}" ]]; then
      if sudo -u "$SUDO_USER" -H env OLLAMA_HOST="$OLLAMA_HOST" ollama show "$model" >/dev/null 2>&1; then
        echo "Model $model already present; skipping pull"
      else
        sudo -u "$SUDO_USER" -H env OLLAMA_HOST="$OLLAMA_HOST" ollama pull "$model" || true
      fi
    else
      if env OLLAMA_HOST="$OLLAMA_HOST" ollama show "$model" >/dev/null 2>&1; then
        echo "Model $model already present; skipping pull"
      else
        env OLLAMA_HOST="$OLLAMA_HOST" ollama pull "$model" || true
      fi
    fi
  }
  check_or_pull gpt-oss:20b &
  check_or_pull gpt-oss:120b &
fi

cd "$REPO_ROOT"
python -m uvicorn lan_modder.app:app --host "$HOST" --port "$PORT" --reload
