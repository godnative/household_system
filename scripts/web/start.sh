#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")/../.." && pwd)/scripts/web/common.sh"

require_command pnpm
if [[ ! -x "$ROOT_DIR/backend/.venv/bin/uvicorn" ]]; then
  log '未找到 backend/.venv/bin/uvicorn，请先执行 bash scripts/web/setup.sh'
  exit 1
fi

start_backend
start_frontend
status_all

log "后端地址: http://127.0.0.1:${BACKEND_PORT}"
log "前端地址: http://127.0.0.1:${FRONTEND_PORT}"
