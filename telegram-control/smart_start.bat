@echo off
chcp 65001 >nul
title Claude Code Bot 智能启动

cls
echo ========================================
echo   Claude Code Bot 智能启动系统
echo ========================================
echo.
echo 正在检查运行状态...
echo.

REM "检查Python进程"
tasklist /FI "IMAGENAME eq pythonw.exe" 2>nul | find /I /N "pythonw.exe">nul
if "%ERRORLEVEL%"=="0" (
    echo [警告] 检测到Bot正在运行
    echo.
    echo [1] 停止旧实例并重新启动
    echo [2] 取消操作
    echo.
    choice /C 12 /N /M "请选择 (1或2): "

    if errorlevel 2 (
        echo.
        echo 操作已取消
        pause
        exit /b
    )

    echo.
    echo [*] 正在停止旧实例...
    taskkill /F /IM pythonw.exe >nul 2>&1
    taskkill /F /IM python.exe >nul 2>&1
    timeout /t 3 /nobreak >nul
    echo [OK] 旧实例已停止
    echo.
)

echo [*] 启动Bot系统...
echo.

cd /d "%~dp0"

echo [1/2] 启动AI监听器...
start "Claude监听器" /MIN pythonw claude_smart_listener.py
timeout /t 3 /nobreak >nul

echo [2/2] 启动Telegram Bot...
start "Telegram Bot" /MIN pythonw bot_forward.py
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   系统已成功启动！
echo ========================================
echo.
echo 功能:
echo   - 文本操作: 创建/读取/写入文件
echo   - 文件传输: 支持所有格式（最大100MB）
echo   - AI助手: 自然语言交互
echo.
echo 停止系统: 运行 stop_all.bat
echo.
echo ========================================
pause
