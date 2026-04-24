#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")/../.." && pwd)/scripts/pyqt/common.sh"

require_command python3

if [[ ! -d "$PYQT_VENV_DIR" ]]; then
  log '创建 PyQt5 虚拟环境 .venv-pyqt'
  python3 -m venv "$PYQT_VENV_DIR"
fi

log '安装 PyQt5 项目依赖'
"$PYQT_VENV_DIR/bin/pip" install -r "$ROOT_DIR/requirements.txt"

if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  log '当前未检测到图形界面环境，仅完成依赖安装；启动桌面端前请确认 DISPLAY 或 WAYLAND_DISPLAY 可用。'
fi

log 'PyQt5 环境准备完成'
log '启动命令: bash scripts/pyqt/start.sh'
