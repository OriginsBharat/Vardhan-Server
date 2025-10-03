@echo off
REM This script is the master controller for your AI World.
REM It includes one-time setup instructions and the commands to launch the world.

REM --- ONE-TIME SETUP INSTRUCTIONS ---
REM You only need to follow these manual steps ONCE.
echo ---------------------------------------------------------------------
echo ONE-TIME SETUP INSTRUCTIONS
echo ---------------------------------------------------------------------
echo.
echo [Step 1] Install Python Libraries:
pip install -r requirements.txt
echo.
echo [Step 2] Install Ollama (The AI's Brain):
echo    - Go to https://ollama.com/download and install Ollama for Windows.
echo    - After installing, open a NEW command prompt and run:
echo      ollama pull llama3:latest
echo      (You can replace 'llama3:latest' with any other model you prefer)
echo.
echo [Step 3] Install ComfyUI (The AI's Art Studio):
echo    - Go to https://github.com/comfyanonymous/ComfyUI/releases
echo    - Download the latest 'windows_portable_nvidia_cu121_or_cpu.7z' file.
echo    - Extract it somewhere permanent (e.g., C:\ComfyUI).
echo.
echo [Step 4] Install FFmpeg (The AI's Voice):
echo    - Go to https://www.gyan.dev/ffmpeg/builds/ and download the 'essentials' .7z file.
echo    - Extract it somewhere permanent.
echo    - Find the 'bin' folder inside and add its full path to your system's PATH environment variable.
echo.
echo ---------------------------------------------------------------------
echo SETUP INSTRUCTIONS FINISHED.
echo If you have completed the setup, you can close this window.
echo From now on, you will run 'invisible_launcher.vbs' to start the world.
echo ---------------------------------------------------------------------
echo.
pause

REM --- LAUNCH SEQUENCE ---
REM This part of the script is what 'invisible_launcher.vbs' will run silently.
REM It starts each component with delays to prevent errors.

REM Create profiles directory if it doesn't exist
if not exist "profiles" mkdir profiles

REM Start Ollama and wait 15 seconds.
start "Ollama" /B ollama serve
timeout /t 15 /nobreak > nul

REM Start ComfyUI and wait 30 seconds.
REM !!! IMPORTANT !!! You must change the path below to match where YOU extracted ComfyUI.
set COMFYUI_PATH="C:\Path\To\Your\ComfyUI_windows_portable"
start "ComfyUI" /B /D %COMFYUI_PATH% run_nvidia_gpu.bat --listen
timeout /t 30 /nobreak > nul

REM Start the main bot.
start "AI World Bot" /B py -u main.py

ECHO AI World has been launched.