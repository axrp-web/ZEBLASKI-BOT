@echo off
title Remove 24/7 Auto-Start - ZEBLASKI OFFICIAL BOT
cls
echo ========================================================
echo       REMOVE 24/7 AUTO-START FROM WINDOWS STARTUP
echo ========================================================
echo.

set "SHORTCUT_PATH=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\ZeblaskiOfficialBot.lnk"

if exist "%SHORTCUT_PATH%" (
    del /f /q "%SHORTCUT_PATH%"
    echo [+] Successfully removed ZeblaskiOfficialBot from Windows Startup!
) else (
    echo [-] No startup shortcut was found in Windows Startup.
)

echo.
call "%~dp0stop_bot.bat"
