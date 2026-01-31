$sh = New-Object -ComObject WScript.Shell
$sc = $sh.CreateShortcut("C:\Users\manke\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Claude Code Bot.lnk")
Write-Host "快捷方式配置:"
Write-Host "TargetPath: $($sc.TargetPath)"
Write-Host "WorkingDirectory: $($sc.WorkingDirectory)"
Write-Host "WindowStyle: $($sc.WindowStyle)"
