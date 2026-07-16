#!/bin/bash
# Unix startup script for local development.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$BACKEND_DIR/venv"
ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"

echo "--------------------------------------------------------"
echo "AAA - Adaptive AI FilmAura: Local Dev Startup (Unix)"
echo "--------------------------------------------------------"

# Verify virtual environment exists
if [ ! -f "$ACTIVATE_SCRIPT" ]; then
    echo "Error: Virtual environment activation script not found at $ACTIVATE_SCRIPT. Please ensure venv is configured."
    exit 1
fi

# Navigate to backend directory
cd "$BACKEND_DIR" || exit 1

# Ensure .env file exists
if [ ! -f ".env" ]; then
    echo "[!] .env file not found. Initializing from .env.example..."
    cp .env.example .env
fi

# Activate venv
echo "[*] Activating Python virtual environment..."
source "$ACTIVATE_SCRIPT"

# Run database migrations
echo "[*] Checking and executing database migrations..."
if alembic upgrade head; then
    echo "[*] Migrations check complete"
else
    echo "[!] Alembic migration failed. If database container is offline, this is normal."
fi

# Run FastAPI server
echo "[*] Starting Uvicorn reload server at http://127.0.0.1:8000..."
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
