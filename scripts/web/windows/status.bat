@echo off
setlocal enabledelayedexpansion

set "APP_HOME=%LOCALAPPDATA%\HouseholdSystemWeb"
set "PID_FILE=%APP_HOME%\runtime\pids\backend.pid"
set "BACKEND_PORT=8000"

if exist "%PID_FILE%" (
  set /p TARGET_PID=<"%PID_FILE%"
  tasklist /FI "PID eq !TARGET_PID!" | findstr /R /C:" !TARGET_PID! " >nul 2>&1
  if not errorlevel 1 (
    echo [web] 服务运行中，PID=!TARGET_PID!，端口=%BACKEND_PORT%
    exit /b 0
  )
)

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
  echo [web] 服务运行中，PID=%%P，端口=%BACKEND_PORT%
  exit /b 0
)

echo [web] 服务未运行。
exit /b 1
