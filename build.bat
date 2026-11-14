@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title SNAKEY build

echo ============================================
echo   SNAKEY - сборка игры в SNAKEY.exe
echo ============================================
echo.

rem --- 1. Проверяем Python ---
where python >nul 2>nul
if errorlevel 1 (
    echo [ОШИБКА] Python не найден.
    echo Установи его с https://www.python.org/downloads/
    echo и отметь галочку "Add python.exe to PATH" при установке.
    pause
    exit /b 1
)

rem --- 2. Проверяем/ставим PyInstaller ---
python -c "import PyInstaller" >nul 2>nul
if errorlevel 1 (
    echo [i] PyInstaller не найден, устанавливаю...
    python -m pip install --quiet pyinstaller
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить PyInstaller. Проверь интернет и повтори.
        pause
        exit /b 1
    )
)

rem --- 3. Собираем exe ---
echo [1/3] Собираю SNAKEY.exe...
set "ICON_ARG="
if exist assets\snakey.ico set "ICON_ARG=--icon assets\snakey.ico"
python -m PyInstaller --clean --noconfirm --onefile --windowed --name SNAKEY %ICON_ARG% snakey_main.py
if errorlevel 1 (
    echo [ОШИБКА] Сборка не удалась - смотри сообщения выше.
    pause
    exit /b 1
)

rem --- 4. Кладём exe рядом с кодом и ресурсами ---
echo [2/3] Копирую SNAKEY.exe в папку игры...
move /y "dist\SNAKEY.exe" "SNAKEY.exe" >nul
if errorlevel 1 (
    echo [ОШИБКА] Не удалось переместить dist\SNAKEY.exe - возможно, игра запущена. Закрой SNAKEY.exe и запусти build.bat ещё раз.
    pause
    exit /b 1
)

rem --- 5. Чистим временные папки сборки ---
echo [3/3] Чищу временные файлы сборки...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist SNAKEY.spec del /q SNAKEY.spec

echo.
echo ============================================
echo   Готово! SNAKEY.exe лежит в папке игры.
echo.
echo   Папка assets\ должна остаться рядом с exe:
echo   звуки, иконка и VERSION читаются из неё,
echo   поэтому звуки/музыку можно менять и без
echo   пересборки - просто подмени файлы.
echo ============================================
echo.
pause
