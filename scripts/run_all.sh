#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_PORT="${BACKEND_PORT:-8000}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it first: https://docs.astral.sh/uv/" >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required. Install Node.js first." >&2
  exit 1
fi

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID"
  fi
  if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID"
  fi
}

trap cleanup INT TERM EXIT

# Uvicorn CLI usage per Context7: /encode/uvicorn (run app:app with --reload).
(
  cd "$ROOT_DIR"
  uv run uvicorn src.api.server:app --reload --port "$BACKEND_PORT"
) &
BACKEND_PID=$!

# Next.js dev server per Context7: /vercel/next.js (npm run dev).
(
  cd "$ROOT_DIR/frontend"
  NEXT_PUBLIC_API_BASE="http://localhost:${BACKEND_PORT}" \
  NEXT_PUBLIC_WS_URL="ws://localhost:${BACKEND_PORT}/ws" \
  npm run dev
) &
FRONTEND_PID=$!

wait
