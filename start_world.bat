@echo off
REM This is the master launch script for the My AI World project.
REM It is run silently by the invisible_launcher.vbs script on Windows startup.
REM It starts all necessary AI services and the main bot application as background processes.

ECHO Starting AI World services in the background...

REM --- Get the directory of the current script ---
SET "SCRIPT_DIR=%~dp0"
CD /D "%SCRIPT_DIR%"

REM --- Start Ollama AI (Text Generation) ---
REM Ollama is typically started as a system service upon installation.
REM This command ensures it's running if it wasn't started automatically.
ECHO Checking Ollama service...
start "" /B ollama serve > nul 2>&1

REM --- Start ComfyUI (Art Generation) ---
REM This requires the user to have set the path in the .env file.
REM We will read the path from the .env file.
FOR /F "tokens=1,* delims==" %%A IN ('.env') DO (
    IF "%%A"=="COMFYUI_PATH" SET COMFYUI_PATH=%%B
)
IF DEFINED COMFYUI_PATH (
    ECHO Starting ComfyUI server...
    start "" /B /D "%COMFYUI_PATH%" run_nvidia_gpu.bat --listen > nul 2>&1
) ELSE (
    ECHO WARNING: COMFYUI_PATH not set in .env file. Art generation will not work.
)

REM --- Voice Generation (Chatterbox) ---
REM The new Chatterbox voice engine is a Python library and does not require a separate server.
REM It will be initialized directly by the main bot application.

REM --- Wait for AI services to initialize ---
ECHO Waiting for AI services to come online...
timeout /t 45 /nobreak > nul

REM --- Start the Main Bot Application ---
ECHO Starting the main bot using the local virtual environment...
start "" /B venv\Scripts\python.exe -m src.main > nul 2>&1

ECHO All services have been launched in the background. The world is now online.