@echo off
REM This script now waits for each component to be ready before starting the next.

REM Ollama is now a Windows service and starts automatically. This line is no longer needed.
REM start "Ollama" /B ollama serve
REM timeout /t 15 /nobreak > nul

REM Start ComfyUI Art Generator and wait 30 seconds for it to initialize.
start "ComfyUI" /B /D "C:\Users\yashv\Downloads\ComfyUI_windows_portable_nvidia_cu121_or_cpu\ComfyUI_windows_portable" run_nvidia_gpu.bat
timeout /t 30 /nobreak > nul

REM Start the main AI Bot.
start "AI World Bot" /B py -u main.py