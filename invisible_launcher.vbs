' This VBScript runs the main startup batch file silently, without any visible command window.
' A shortcut to this file will be placed in the user's Startup folder by the setup script.
CreateObject("Wscript.Shell").Run "start_world.bat", 0, False