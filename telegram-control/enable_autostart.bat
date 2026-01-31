@echo off
chcp 65001 >nul
echo ========================================
echo   设置 Telegram Bot 开机自启
echo ========================================
echo.

cd /d C:\Users\manke\.claude\skills\telegram-control

echo [*] 创建开机自启快捷方式...

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Claude Code Bot.lnk'); $Shortcut.TargetPath = 'C:\Users\manke\.claude\skills\telegram-control\start_all.bat'; $Shortcut.WorkingDirectory = 'C:\Users\manke\.claude\skills\telegram-control'; $Shortcut.WindowStyle = 7; $Shortcut.Save()"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] 开机自启已设置成功！
    echo.
    echo 快捷方式已创建到启动文件夹:
    echo %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Claude Code Bot.lnk
    echo.
    echo 下次开机时会自动启动 Bot 系统
    echo.
) else (
    echo.
    echo [X] 设置失败，请检查权限
    echo.
)

pause
