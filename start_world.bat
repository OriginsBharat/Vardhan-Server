@echo off
REM My AI World - Silent Launcher
REM This script is executed by invisible_launcher.vbs to start the world silently.

ECHO Starting My AI World...

REM Get the directory of the batch file
SET "BATCH_DIR=%~dp0"
SET "COMFYUI_PATH_FILE=%BATCH_DIR%data\.comfyui_path"

REM Check if the ComfyUI path file exists
IF NOT EXIST "%COMFYUI_PATH_FILE%" (
    ECHO ERROR: ComfyUI path not set. Please run SETUP_THE_WORLD.py first.
    pause
    exit /b
)

REM Read the ComfyUI path from the file
SET /p COMFYUI_PATH=<"%COMFYUI_PATH_FILE%"

REM 1. Start Ollama Server (usually runs as a background service after installation)
ECHO Ensuring Ollama is running...
REM We assume Ollama is already running as a system tray application.
REM If not, the user would need to start it manually. The setup script will instruct this.
tasklist /fi "imagename eq ollama.exe" | find "ollama.exe" >nul
IF ERRORLEVEL 1 (
    ECHO Ollama is not running. Please start the Ollama application.
) ELSE (
    ECHO Ollama is running.
)

REM 2. Start ComfyUI Server
ECHO Starting ComfyUI server in the background...
START "ComfyUI" /B python "%COMFYUI_PATH%\main.py" --listen

REM A short delay to allow the server to initialize before the bot tries to connect
timeout /t 15

REM 3. Start the main Discord Bot Application
ECHO Starting the main bot application...
cd /d "%BATCH_DIR%"
python src/main.py

ECHO The world has stopped.