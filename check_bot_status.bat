@echo off
title Check Bot Status - ZEBLASKI OFFICIAL BOT
cls
echo ========================================================
echo        CHECKING ZEBLASKI OFFICIAL BOT STATUS
echo ========================================================
echo.

powershell -NoProfile -Command ^
    "$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*bot.py*' }; " ^
    "if ($procs) { " ^
    "    Write-Host 'STATUS: [ONLINE - RUNNING IN BACKGROUND]' -ForegroundColor Green; " ^
    "    $procs | ForEach-Object { " ^
    "        $p = Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue; " ^
    "        $mem = if ($p) { [math]::Round($p.WorkingSet64 / 1MB, 2) } else { 'N/A' }; " ^
    "        Write-Host ('  Process PID : ' + $_.ProcessId); " ^
    "        Write-Host ('  Memory Usage: ' + $mem + ' MB'); " ^
    "    }; " ^
    "} else { " ^
    "    Write-Host 'STATUS: [OFFLINE - NOT RUNNING]' -ForegroundColor Red; " ^
    "}"

echo.
if exist "bot_runtime.log" (
    echo [Recent Logs from bot_runtime.log]:
    powershell -NoProfile -Command "Get-Content bot_runtime.log -Tail 10 -ErrorAction SilentlyContinue"
)

echo.
pause
