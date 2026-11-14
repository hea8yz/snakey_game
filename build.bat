@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SNAKEY build

echo ============================================
echo   SNAKEY - building SNAKEY.exe
echo ============================================
echo.

rem --- 1. Check Python (real run, not just "where") ---
python --version >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found or not working.
    echo.
    echo Install Python from https://www.python.org/downloads/
    echo and CHECK the box "Add python.exe to PATH" during setup.
    echo If you installed Python from Microsoft Store - uninstall it
    echo and use the python.org installer instead.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo [i] Found %%v

rem --- 2. Check / install PyInstaller ---
python -c "import PyInstaller" >nul 2>nul
if errorlevel 1 (
    echo [i] PyInstaller not found, installing...
    python -m pip install --quiet pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller. Check internet and try again.
        echo.
        pause
        exit /b 1
    )
)

rem --- 3. Build the exe ---
echo [1/3] Building SNAKEY.exe - this takes about a minute...
set "ICON_ARG="
if exist assets\snakey.ico set "ICON_ARG=--icon assets\snakey.ico"
python -m PyInstaller --clean --noconfirm --onefile --windowed --name SNAKEY %ICON_ARG% snakey_main.py
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed - see PyInstaller messages above.
    echo.
    pause
    exit /b 1
)

rem --- 4. Move the exe next to the game files ---
echo [2/3] Moving SNAKEY.exe into the game folder...
move /y "dist\SNAKEY.exe" "SNAKEY.exe" >nul
if errorlevel 1 (
    echo [ERROR] Could not move dist\SNAKEY.exe into the game folder.
    echo Most likely the game is running right now - close SNAKEY.exe and run build.bat again.
    echo.
    pause
    exit /b 1
)

rem --- 5. Clean up temporary build files ---
echo [3/3] Cleaning temporary build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist SNAKEY.spec del /q SNAKEY.spec

echo.
if exist SNAKEY.exe (
    echo ============================================
    echo   SUCCESS! SNAKEY.exe is in the game folder,
    echo   next to snakey_main.py and assets\.
    echo.
    echo   Keep the assets\ folder next to the exe:
    echo   sounds, icon and VERSION are read from it.
    echo ============================================
) else (
    echo [WARNING] exe was built but not found in the folder.
    echo Check your antivirus - it may have quarantined SNAKEY.exe.
)
echo.
pause
