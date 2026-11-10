@echo off
cd /d "%~dp0"

:loop
echo [%date% %time%] Starting Zeblaski Official Bot... >> "bot_runtime.log"

:: Check standard python or local python 3.12
where python >nul 2>nul
if %errorlevel% equ 0 (
    python bot.py >> "bot_runtime.log" 2>&1
) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" bot.py >> "bot_runtime.log" 2>&1
) else (
    echo [%date% %time%] Python not found! Exiting loop. >> "bot_runtime.log"
    exit /b 1
)

echo [%date% %time%] Bot stopped or crashed. Restarting in 5 seconds... >> "bot_runtime.log"
timeout /t 5 /nobreak >nul
goto loop
