#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/runtime/pyqt"
LOG_DIR="$RUNTIME_DIR/logs"
PID_DIR="$RUNTIME_DIR/pids"
APP_PID_FILE="$PID_DIR/app.pid"
APP_LOG_FILE="$LOG_DIR/app.log"
PYQT_VENV_DIR="$ROOT_DIR/.venv-pyqt"

mkdir -p "$LOG_DIR" "$PID_DIR"

log() {
  printf '[pyqt] %s\n' "$1"
}

require_command() {
  local command_name="$1"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    log "缺少命令: $command_name"
    exit 1
  fi
}

is_pid_running() {
  local pid="$1"
  kill -0 "$pid" >/dev/null 2>&1
}

cleanup_stale_pid() {
  if [[ -f "$APP_PID_FILE" ]]; then
    local pid
    pid="$(cat "$APP_PID_FILE")"
    if [[ -n "$pid" ]] && is_pid_running "$pid"; then
      return 0
    fi
    rm -f "$APP_PID_FILE"
  fi
  return 1
}

stop_app() {
  if [[ ! -f "$APP_PID_FILE" ]]; then
    log '桌面端未运行。'
    return 0
  fi

  local pid
  pid="$(cat "$APP_PID_FILE")"
  if [[ -z "$pid" ]] || ! is_pid_running "$pid"; then
    rm -f "$APP_PID_FILE"
    log '桌面端 PID 文件已清理。'
    return 0
  fi

  kill "$pid" >/dev/null 2>&1 || true
  for _ in 1 2 3 4 5; do
    if ! is_pid_running "$pid"; then
      rm -f "$APP_PID_FILE"
      log '桌面端已停止。'
      return 0
    fi
    sleep 1
  done

  kill -9 "$pid" >/dev/null 2>&1 || true
  rm -f "$APP_PID_FILE"
  log '桌面端已强制停止。'
}

status_app() {
  if cleanup_stale_pid; then
    log "桌面端运行中，PID=$(cat "$APP_PID_FILE")"
  else
    log '桌面端未运行。'
  fi

  if [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]]; then
    log '检测到图形界面环境。'
  else
    log '未检测到 DISPLAY/WAYLAND_DISPLAY，当前环境可能无法启动 GUI。'
  fi
}
