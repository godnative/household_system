@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..\..") do set "ROOT_DIR=%%~fI"
set "APP_HOME=%LOCALAPPDATA%\HouseholdSystemWeb"
set "RUNTIME_DIR=%APP_HOME%\runtime"
set "LOG_DIR=%RUNTIME_DIR%\logs"
set "PID_DIR=%RUNTIME_DIR%\pids"
set "PID_FILE=%PID_DIR%\backend.pid"
set "BACKEND_LOG=%LOG_DIR%\backend.log"
set "BACKEND_PORT=8000"

if not exist "%APP_HOME%" mkdir "%APP_HOME%"
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%PID_DIR%" mkdir "%PID_DIR%"
if not exist "%APP_HOME%\data" mkdir "%APP_HOME%\data"
if not exist "%APP_HOME%\uploads" mkdir "%APP_HOME%\uploads"

if exist "%PID_FILE%" (
  set /p EXISTING_PID=<"%PID_FILE%"
  tasklist /FI "PID eq !EXISTING_PID!" | findstr /R /C:" !EXISTING_PID! " >nul 2>&1
  if not errorlevel 1 (
    echo [web] 服务已在运行，PID=!EXISTING_PID!
    start "" "http://127.0.0.1:%BACKEND_PORT%"
    exit /b 0
  )
  del "%PID_FILE%" >nul 2>&1
)

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
  echo [web] 端口 %BACKEND_PORT% 已被占用，请先关闭现有服务。
  exit /b 1
)

set "SERVE_FRONTEND=1"
set "APP_ENV=production"
set "RUNTIME_BASE_DIR=%APP_HOME%"
set "DATABASE_URL=sqlite:///%APP_HOME:\=/%/data/household_system_web.db"
set "UPLOAD_DIR=uploads"
set "FRONTEND_DIST_DIR=%ROOT_DIR%\frontend\dist"
set "BACKEND_ENTRY=%ROOT_DIR%\dist\windows-web\backend\household-system-api.exe"

if not exist "%BACKEND_ENTRY%" (
  echo [web] 未找到后端可执行文件：%BACKEND_ENTRY%
  exit /b 1
)

start "HouseholdSystemWeb" /B "%BACKEND_ENTRY%" > "%BACKEND_LOG%" 2>&1
set "LATEST_PID="
for /l %%I in (1,1,10) do (
  for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
    set "LATEST_PID=%%P"
  )
  if defined LATEST_PID goto pid_ready
  timeout /t 1 /nobreak >nul
)

echo [web] 服务启动失败，请检查日志：%BACKEND_LOG%
exit /b 1

:pid_ready
echo !LATEST_PID!>"%PID_FILE%"
start "" "http://127.0.0.1:%BACKEND_PORT%"
echo [web] 服务已启动，PID=!LATEST_PID!
