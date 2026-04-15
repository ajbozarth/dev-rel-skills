#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"

# Install dependencies if needed
if [ ! -d "$DIR/.venv" ]; then
  echo "Installing Python dependencies..."
  (cd "$DIR" && uv sync)
fi

if [ ! -d "$DIR/frontend/node_modules" ]; then
  echo "Installing frontend dependencies..."
  (cd "$DIR/frontend" && npm install)
fi

# Start backend and frontend, kill both on exit
trap 'kill 0' EXIT

echo "Starting backend on http://localhost:8000 ..."
(cd "$DIR" && uv run uvicorn backend.main:app --reload --port 8000) &

echo "Starting frontend on http://localhost:5173 ..."
(cd "$DIR/frontend" && npm run dev) &

wait
