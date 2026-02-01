@echo off
chcp 65001 >nul
title Bot状态检查

cls
echo ========================================
echo   Bot运行状态检查
echo ========================================
echo.

tasklist /FI "IMAGENAME eq pythonw.exe" 2>nul | find /I /N "pythonw.exe">nul
if "%ERRORLEVEL%"=="1" (
    echo [状态] 未运行
    echo.
    echo 未检测到Bot进程
    echo.
    echo 要启动Bot，请运行: smart_start.bat
) else (
    echo [状态] 正在运行
    echo.
    echo 运行中的Python进程:
    echo.
    tasklist /FI "IMAGENAME eq pythonw.exe" /FO TABLE
    echo.
    echo Bot功能:
    echo   - Telegram远程控制
    echo   - 文件传输
    echo   - AI助手
    echo.
    echo 要停止Bot，请运行: smart_stop.bat
)

echo.
echo ========================================
pause
