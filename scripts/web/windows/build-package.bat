@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "ROOT_DIR=%%~fI"
set "OUTPUT_DIR=%ROOT_DIR%\dist\windows-web"
set "FRONTEND_DIST=%ROOT_DIR%\frontend\dist"
set "BACKEND_DIST=%OUTPUT_DIR%\backend"

where pnpm >nul 2>&1 || (echo [pack] 缺少 pnpm & exit /b 1)
where pyinstaller >nul 2>&1 || (echo [pack] 缺少 pyinstaller & exit /b 1)

if exist "%OUTPUT_DIR%" rmdir /s /q "%OUTPUT_DIR%"
mkdir "%BACKEND_DIST%"

pushd "%ROOT_DIR%\frontend"
call pnpm install --frozen-lockfile || exit /b 1
call pnpm build || exit /b 1
popd

pushd "%ROOT_DIR%\backend"
pyinstaller --noconfirm --clean --name household-system-api --distpath "%BACKEND_DIST%" --workpath "%ROOT_DIR%\dist\windows-web\build" --specpath "%ROOT_DIR%\dist\windows-web\spec" --paths "%ROOT_DIR%\backend" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 || exit /b 1
popd

xcopy "%FRONTEND_DIST%" "%OUTPUT_DIR%\frontend\dist\" /E /I /Y >nul
xcopy "%ROOT_DIR%\scripts\web\windows" "%OUTPUT_DIR%\scripts\" /E /I /Y >nul
copy "%ROOT_DIR%\backend\.env.example" "%OUTPUT_DIR%\backend\.env.example" >nul
copy "%ROOT_DIR%\backend\requirements-prod.txt" "%OUTPUT_DIR%\backend\requirements-prod.txt" >nul
copy "%ROOT_DIR%\scripts\web\windows\HouseholdSystemWeb.iss" "%OUTPUT_DIR%\HouseholdSystemWeb.iss" >nul

echo [pack] Windows 离线发布目录已生成：%OUTPUT_DIR%
