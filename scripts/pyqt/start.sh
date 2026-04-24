#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")/../.." && pwd)/scripts/pyqt/common.sh"

if [[ ! -x "$PYQT_VENV_DIR/bin/python" ]]; then
  log '未找到 .venv-pyqt，请先执行 bash scripts/pyqt/setup.sh'
  exit 1
fi

cleanup_stale_pid && {
  log '桌面端已在运行。'
  status_app
  exit 0
}

if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  log '未检测到 DISPLAY/WAYLAND_DISPLAY，无法启动桌面端 GUI。'
  exit 1
fi

APP_ARGS=()
if [[ "${1:-}" == "--debug" ]]; then
  APP_ARGS+=("--debug")
fi

nohup "$PYQT_VENV_DIR/bin/python" -m src.app "${APP_ARGS[@]}" >"$APP_LOG_FILE" 2>&1 &
echo $! > "$APP_PID_FILE"
log "桌面端已启动，PID=$(cat "$APP_PID_FILE")，日志: $APP_LOG_FILE"
