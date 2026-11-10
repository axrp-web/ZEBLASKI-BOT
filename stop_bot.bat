@echo off
title Stop Background Bot - ZEBLASKI OFFICIAL BOT
cls
echo ========================================================
echo       STOPPING ZEBLASKI OFFICIAL BOT BACKGROUND PROCESS
echo ========================================================
echo.

echo [*] Terminating bot background processes...
powershell -NoProfile -Command ^
    "$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*bot.py*' }; " ^
    "if ($procs) { " ^
    "    $procs | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host ('[+] Stopped process PID: ' + $_.ProcessId) }; " ^
    "} else { " ^
    "    Write-Host '[-] No running bot.py processes found.'; " ^
    "}"

echo.
echo [*] Terminating restart loops if any...
taskkill /F /FI "WINDOWTITLE eq Zeblaski Official Bot Loop*" >nul 2>nul

echo [+] Finished.
echo.
pause
