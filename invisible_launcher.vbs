' My AI World - Invisible Launcher
' This script starts the world without any visible command window.

Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c start_world.bat", 0
Set WshShell = Nothing