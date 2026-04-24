#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf '[web] 缺少命令: %s\n' "$1"
    exit 1
  fi
}

require_command python3
require_command node
require_command pnpm

mkdir -p "$ROOT_DIR/runtime/web/logs" "$ROOT_DIR/runtime/web/pids"

if [[ ! -d "$ROOT_DIR/backend/.venv" ]]; then
  printf '[web] 创建后端虚拟环境 backend/.venv\n'
  python3 -m venv "$ROOT_DIR/backend/.venv"
fi

printf '[web] 安装后端依赖\n'
"$ROOT_DIR/backend/.venv/bin/pip" install -r "$ROOT_DIR/backend/requirements.txt"

if [[ ! -f "$ROOT_DIR/backend/.env" ]]; then
  cp "$ROOT_DIR/backend/.env.example" "$ROOT_DIR/backend/.env"
  printf '[web] 已创建 backend/.env，默认使用本地 SQLite 开发配置\n'
else
  printf '[web] 检测到已有 backend/.env，保留现有配置不覆盖\n'
fi

printf '[web] 安装前端依赖\n'
(cd "$ROOT_DIR/frontend" && pnpm install)

if [[ ! -f "$ROOT_DIR/frontend/.env" ]]; then
  cp "$ROOT_DIR/frontend/.env.example" "$ROOT_DIR/frontend/.env"
  printf '[web] 已创建 frontend/.env\n'
fi

printf '[web] Web 环境准备完成\n'
printf '[web] 默认本地脚本验收使用 SQLite；如需 PostgreSQL，请手动修改 backend/.env\n'
printf '[web] 启动命令: bash scripts/web/start.sh\n'
