@echo off
chcp 65001 >nul
title Claude Code Bot 智能停止

cls
echo ========================================
echo   Claude Code Bot 停止系统
echo ========================================
echo.

REM "检查是否有Python进程运行"
tasklist /FI "IMAGENAME eq pythonw.exe" 2>nul | find /I /N "pythonw.exe">nul
if "%ERRORLEVEL%"=="1" (
    echo [提示] Bot未运行
    echo.
    pause
    exit /b
)

echo [*] 正在停止Bot进程...
echo.

REM "优雅停止：先尝试正常关闭"
taskkill /IM pythonw.exe >nul 2>&1
taskkill /IM python.exe >nul 2>&1

REM "等待3秒让进程优雅退出"
timeout /t 3 /nobreak >nul

REM "检查是否还有残留"
tasklist /FI "IMAGENAME eq pythonw.exe" 2>nul | find /I /N "pythonw.exe">nul
if "%ERRORLEVEL%"=="0" (
    echo [!] 检测到残留进程，强制终止...
    taskkill /F /IM pythonw.exe >nul 2>&1
    taskkill /F /IM python.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo [OK] Bot已完全停止
echo.
echo ========================================
pause
