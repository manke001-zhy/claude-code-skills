@echo off
chcp 65001 >nul
echo ========================================
echo   取消 Telegram Bot 开机自启
echo ========================================
echo.

cd /d C:\Users\manke\.claude\skills\telegram-control

echo [*] 删除开机自启快捷方式...

if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Claude Code Bot.lnk" (
    del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Claude Code Bot.lnk"
    echo.
    echo [OK] 已取消开机自启
    echo.
    echo 下次开机时不会自动启动 Bot 系统
    echo.
) else (
    echo.
    echo [!] 未找到开机自启快捷方式
    echo 可能之前没有设置过开机自启
    echo.
)

pause
