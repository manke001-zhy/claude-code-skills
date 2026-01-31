@echo off
chcp 65001 >nul
echo ========================================
echo   启动 Claude Code Bot 完整系统
echo ========================================
echo.

cd /d C:\Users\manke\.claude\skills\telegram-control

echo.
echo [*] 清理旧进程...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo [1/2] 启动 AI监听器...
start "Claude监听器" /MIN pythonw claude_smart_listener.py
timeout /t 3 /nobreak >nul

echo [2/2] 启动 Telegram Bot...
start "Telegram Bot" /MIN pythonw bot_forward.py
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   系统已启动！
echo ========================================
echo.
echo 功能:
echo.
echo 📝 文本操作:
echo   - 创建文件: test.txt写入hello
echo   - 读取文件: 读取test.txt
echo   - 写入内容: ai助手.txt写入123456
echo.
echo 📎 文件接收 (支持所有格式):
echo   - 🎬 视频: mp4, avi, mkv, mov (最大100MB)
echo   - 🎵 音频: mp3, wav, flac (最大100MB)
echo   - 🖼️  图片: jpg, png, gif
echo   - 📄 文档: pdf, docx, xlsx
echo   - 📦 压缩: zip, rar, 7z
echo.
echo 使用提示:
echo - 直接在Telegram中发送文件
echo - 用自然语言描述需求
echo - Bot会理解并执行
echo.
echo 停止系统: 运行 stop.bat
echo.
echo ========================================
pause
