@echo off
title ZEBLASKI OFFICIAL BOT
cls
echo ========================================================
echo          STARTING ZEBLASKI OFFICIAL BOT
echo ========================================================
echo.

:: Try standard python in PATH first
where python >nul 2>nul
if %errorlevel% equ 0 (
    python bot.py
    goto end
)

:: Fallback to local python 3.12 installation
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" bot.py
    goto end
)

echo [!] Python was not found in PATH or standard installation directory.
echo Please ensure Python 3.10+ is installed.
echo.

:end
pause
