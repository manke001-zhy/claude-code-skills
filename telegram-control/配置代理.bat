@echo off
chcp 65001 >nul
title 配置Bot代理

cls
echo ========================================
echo   Telegram Bot 代理配置向导
echo ========================================
echo.
echo 当前问题: Bot无法访问Telegram服务器
echo 解决方案: 配置代理
echo.
echo ========================================
echo 请选择您的代理类型:
echo.
echo [1] SOCKS5代理 (推荐)
echo     适用于: Clash, V2Ray, SSR等
echo     示例: socks5://127.0.0.1:7890
echo.
echo [2] HTTP代理
echo     适用于: 系统代理, VPN等
echo     示例: http://127.0.0.1:8080
echo.
echo [3] HTTPS代理
echo     示例: https://127.0.0.1:8080
echo.
echo [4] 查看帮助
echo.
echo [5] 取消配置
echo.
echo ========================================

choice /C 12345 /N /M "请选择 (1-5): "

if errorlevel 5 goto :cancel
if errorlevel 4 goto :help
if errorlevel 3 goto :https
if errorlevel 2 goto :http
if errorlevel 1 goto :socks5

:socks5
cls
echo ========================================
echo   配置SOCKS5代理
echo ========================================
echo.
echo 常见端口:
echo   Clash:  7890
echo   V2Ray:  10808
echo   SSR:    1080
echo.
set /p PROXY_PORT="请输入端口号 (直接回车使用默认7890): "
if "%PROXY_PORT%"=="" set PROXY_PORT=7890

set PROXY_URL=socks5://127.0.0.1:%PROXY_PORT%
goto :update_config

:http
cls
echo ========================================
echo   配置HTTP代理
echo ========================================
echo.
set /p PROXY_PORT="请输入端口号: "
if "%PROXY_PORT%"=="" goto :http

set PROXY_URL=http://127.0.0.1:%PROXY_PORT%
goto :update_config

:https
cls
echo ========================================
echo   配置HTTPS代理
echo ========================================
echo.
set /p PROXY_PORT="请输入端口号: "
if "%PROXY_PORT%"=="" goto :https

set PROXY_URL=https://127.0.0.1:%PROXY_PORT%
goto :update_config

:update_config
cls
echo ========================================
echo   更新配置文件
echo ========================================
echo.
echo 代理地址: %PROXY_URL%
echo.

cd /d "%~dp0"

REM "读取原配置"
powershell.exe -NoProfile -Command "$config = Get-Content 'config.local.json' -Raw | ConvertFrom-Json; $config | Add-Member -NotePropertyName 'proxy' -NotePropertyValue '%PROXY_URL%' -Force; $config | ConvertTo-Json -Depth 10 | Set-Content 'config.local.json'"

if errorlevel 1 (
    echo [错误] 配置更新失败
    pause
    exit /b 1
)

echo [成功] 代理已配置
echo.
echo 下一步:
echo   1. 确保代理软件正在运行
echo   2. 重启Bot: 运行 smart_start.bat
echo.
echo ========================================
pause
exit /b 0

:help
start "" notepad.exe "C:\Users\manke\Desktop\代理配置说明.txt"
exit /b 0

:cancel
echo.
echo 操作已取消
pause
exit /b 0
