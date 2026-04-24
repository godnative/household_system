#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

"$ROOT_DIR/scripts/start-backend.sh" &
BACKEND_PID=$!

cleanup() {
  kill $BACKEND_PID 2>/dev/null || true
}

trap cleanup EXIT

"$ROOT_DIR/scripts/start-frontend.sh"
