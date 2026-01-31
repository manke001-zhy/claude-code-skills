Set WshShell = CreateObject("WScript.Shell")
strStartup = WshShell.SpecialFolders("Startup")
Set Shortcut = WshShell.CreateShortcut(strStartup & "\Claude Code Bot.lnk")
Shortcut.TargetPath = "C:\Users\manke\.claude\skills\telegram-control\start_all.bat"
Shortcut.WorkingDirectory = "C:\Users\manke\.claude\skills\telegram-control"
Shortcut.WindowStyle = 7
Shortcut.Save
