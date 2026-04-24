#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")/../.." && pwd)/scripts/web/common.sh"

stop_pid_file "$FRONTEND_PID_FILE" '前端'
stop_pid_file "$BACKEND_PID_FILE" '后端'
