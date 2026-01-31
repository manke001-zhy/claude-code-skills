$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Claude Code Bot.lnk")
$Shortcut.TargetPath = "C:\Users\manke\.claude\skills\telegram-control\start_all.bat"
$Shortcut.WorkingDirectory = "C:\Users\manke\.claude\skills\telegram-control"
$Shortcut.WindowStyle = 7
$Shortcut.Save()

Write-Host "开机自启已设置成功！" -ForegroundColor Green
Write-Host "快捷方式位置: $env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Claude Code Bot.lnk"
