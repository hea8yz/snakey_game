@echo off
setlocal
title SNAKEY updater
echo ===================================
echo   SNAKEY - update from GitHub
echo ===================================
echo.
where powershell >nul 2>nul
if errorlevel 1 (
    echo [ERROR] PowerShell not found on this PC.
    echo Update manually: https://github.com/hea8yz/snakey_game
    echo.
    pause
    exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0snakey_update.ps1"
set "EC=%errorlevel%"
echo.
if not "%EC%"=="0" (
    echo Update finished with errors. See messages above.
    echo If the problem repeats, download files manually:
    echo https://github.com/hea8yz/snakey_game
)
pause
exit /b %EC%
