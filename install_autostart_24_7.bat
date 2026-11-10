@echo off
title Install 24/7 Background Auto-Start - ZEBLASKI OFFICIAL BOT
cls
echo ========================================================
echo     ZEBLASKI OFFICIAL BOT - 24/7 AUTO-START SETUP
echo ========================================================
echo.

where python >nul 2>nul
if %errorlevel% equ 0 (
    python install_autostart.py
    goto end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" install_autostart.py
    goto end
)

echo [!] Python was not found. Please install Python 3.10+.
echo.

:end
echo.
pause
