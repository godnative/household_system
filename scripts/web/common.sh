#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/runtime/web"
LOG_DIR="$RUNTIME_DIR/logs"
PID_DIR="$RUNTIME_DIR/pids"
BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"
BACKEND_LOG_FILE="$LOG_DIR/backend.log"
FRONTEND_LOG_FILE="$LOG_DIR/frontend.log"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

mkdir -p "$LOG_DIR" "$PID_DIR"

log() {
  printf '[web] %s\n' "$1"
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
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if [[ -n "$pid" ]] && is_pid_running "$pid"; then
      return 0
    fi
    rm -f "$pid_file"
  fi
  return 1
}

ensure_port_free() {
  local port="$1"
  local label="$2"
  if ss -ltn "( sport = :$port )" | tail -n +2 | grep -q ":$port"; then
    log "$label 端口 $port 已被占用，请先释放端口后再启动。"
    exit 1
  fi
}

stop_pid_file() {
  local pid_file="$1"
  local label="$2"
  if [[ ! -f "$pid_file" ]]; then
    log "$label 未运行。"
    return 0
  fi

  local pid
  pid="$(cat "$pid_file")"
  if [[ -z "$pid" ]] || ! is_pid_running "$pid"; then
    rm -f "$pid_file"
    log "$label PID 文件已清理。"
    return 0
  fi

  kill "$pid" >/dev/null 2>&1 || true
  for _ in 1 2 3 4 5; do
    if ! is_pid_running "$pid"; then
      rm -f "$pid_file"
      log "$label 已停止。"
      return 0
    fi
    sleep 1
  done

  kill -9 "$pid" >/dev/null 2>&1 || true
  rm -f "$pid_file"
  log "$label 已强制停止。"
}

start_backend() {
  cleanup_stale_pid "$BACKEND_PID_FILE" && {
    log "后端已在运行。"
    return 0
  }

  ensure_port_free "$BACKEND_PORT" '后端'
  nohup "$ROOT_DIR/backend/.venv/bin/uvicorn" app.main:app --app-dir "$ROOT_DIR/backend" --host 0.0.0.0 --port "$BACKEND_PORT" >"$BACKEND_LOG_FILE" 2>&1 &
  echo $! > "$BACKEND_PID_FILE"
  log "后端已启动，PID=$(cat "$BACKEND_PID_FILE")，日志: $BACKEND_LOG_FILE"
}

start_frontend() {
  cleanup_stale_pid "$FRONTEND_PID_FILE" && {
    log "前端已在运行。"
    return 0
  }

  ensure_port_free "$FRONTEND_PORT" '前端'
  nohup bash -lc "cd '$ROOT_DIR/frontend' && pnpm dev --host 0.0.0.0 --port '$FRONTEND_PORT'" >"$FRONTEND_LOG_FILE" 2>&1 &
  echo $! > "$FRONTEND_PID_FILE"
  log "前端已启动，PID=$(cat "$FRONTEND_PID_FILE")，日志: $FRONTEND_LOG_FILE"
}

status_all() {
  if cleanup_stale_pid "$BACKEND_PID_FILE"; then
    log "后端运行中，PID=$(cat "$BACKEND_PID_FILE")，端口=$BACKEND_PORT"
  else
    log '后端未运行。'
  fi

  if cleanup_stale_pid "$FRONTEND_PID_FILE"; then
    log "前端运行中，PID=$(cat "$FRONTEND_PID_FILE")，端口=$FRONTEND_PORT"
  else
    log '前端未运行。'
  fi
}

require_command ss
