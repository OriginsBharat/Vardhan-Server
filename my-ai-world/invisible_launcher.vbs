' This VBScript runs the main startup batch file silently, without any visible command window.
' This is the file you will create a shortcut to in your Startup folder.
CreateObject("Wscript.Shell").Run "start_world.bat", 0, False