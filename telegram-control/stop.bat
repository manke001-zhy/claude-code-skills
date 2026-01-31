@echo off
echo 停止 Claude Code Bot 系统...
taskkill /F /IM python.exe >nul 2>&1
echo.
echo 已停止所有Python进程
pause
