@echo off
setlocal enabledelayedexpansion

set "APP_HOME=%LOCALAPPDATA%\HouseholdSystemWeb"
set "PID_FILE=%APP_HOME%\runtime\pids\backend.pid"
set "BACKEND_PORT=8000"

if exist "%PID_FILE%" (
  set /p TARGET_PID=<"%PID_FILE%"
  if not "!TARGET_PID!"=="" (
    taskkill /PID !TARGET_PID! /T /F >nul 2>&1
  )
  del "%PID_FILE%" >nul 2>&1
)

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
  taskkill /PID %%P /T /F >nul 2>&1
)

echo [web] 服务已关闭。
