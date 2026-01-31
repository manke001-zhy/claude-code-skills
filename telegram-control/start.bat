@echo off
echo ========================================
echo   启动 Claude Code Bot 系统
echo ========================================
echo.

cd /d C:\Users\manke\.claude\skills\telegram-control

echo [1/2] 启动 AI监听器...
start /B python claude_smart_listener.py
timeout /t 2 /nobreak >nul

echo [2/2] 启动 Telegram Bot...
start /B python bot_forward.py
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   系统已启动！
echo ========================================
echo.
echo 监听器和Bot正在后台运行
echo.
echo 功能：
echo - 创建文件: test.txt写入hello
echo - 读取文件: 读取test.txt
echo - 接收文件: 直接发送图片/文件
echo - 列出文件: 桌面有什么
echo.
echo 按任意键关闭此窗口...
pause >nul
