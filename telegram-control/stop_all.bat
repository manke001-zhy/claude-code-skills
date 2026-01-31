@echo off
chcp 65001 >nul
echo 停止 Claude Code Bot 系统...
echo.

taskkill /F /IM pythonw.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1

echo.
echo 系统已停止
echo.
pause
