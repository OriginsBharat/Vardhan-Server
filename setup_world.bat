@echo off
echo =================================================================
echo  Welcome to the One-Time Setup for Your AI World
echo =================================================================
echo.
echo This script will guide you through configuration and set up
echo your world to run automatically and invisibly on PC boot.
echo.
echo Press any key to begin...
pause > nul

cls
echo =================================================================
echo  Step 1 of 3: Creating a Safe Python Environment
echo =================================================================
echo.
echo Creating a local Python virtual environment (venv)...
echo.

python -m venv venv
if %errorlevel% neq 0 (
    echo [FATAL ERROR] Failed to create Python virtual environment.
    echo Please ensure Python 3.10 or higher is installed and in your system's PATH.
    pause
    exit /b 1
)
echo Virtual environment created successfully.
echo.
echo Press any key to continue...
pause > nul

cls
echo =================================================================
echo  Step 2 of 3: Interactive Configuration
echo =================================================================
echo.
echo Launching the interactive Python setup script...
echo Please answer the questions in the window that appears.
echo.

call venv\Scripts\python.exe src\interactive_setup.py
if %errorlevel% neq 0 (
    echo [FATAL ERROR] The interactive setup script failed.
    pause
    exit /b 1
)
echo.
echo Configuration saved successfully.
echo.
echo Press any key to continue...
pause > nul

cls
echo =================================================================
echo  Step 3 of 3: Finalizing Installation
echo =================================================================
echo.
echo Installing required Python packages. This may take several minutes.
echo.

call venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [FATAL ERROR] Python package installation failed. The error is above.
    echo Please check your internet connection and ensure requirements.txt is not corrupted.
    pause
    exit /b 1
)
echo.
echo All packages installed successfully.
echo.
echo Creating and placing the invisible startup script...

:: Create the main startup batch file
(
    echo @echo off
    echo cd /d "%~dp0"
    echo echo Starting Ollama Server...
    echo start /B ollama serve
    echo.
    echo echo Starting ComfyUI Server...
    set /p COMFYUI_PATH=<^< .env
    for /f "tokens=1,* delims==" %%a in ('findstr "COMFYUI_PATH" .env') do set COMFYUI_PATH=%%b
    echo start /B "" "%%COMFYUI_PATH%%\python_embeded\python.exe" -s "%%COMFYUI_PATH%%\main.py" --windows-standalone-build
    echo.
    echo echo Waiting for AI engines to initialize...
    echo timeout /t 20 > nul
    echo.
    echo echo Starting the AI World Bot...
    echo call venv\Scripts\python.exe src\main.py
) > start_world.bat

:: Create the VBScript for invisible execution
(
    echo Set WshShell = CreateObject("WScript.Shell"^)
    echo WshShell.Run "cmd /c \"""%~dp0start_world.bat\""", 0
    echo Set WshShell = Nothing
) > invisible_launcher.vbs

set STARTUP_PATH="%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
copy invisible_launcher.vbs %STARTUP_PATH% > nul
if %errorlevel% neq 0 (
    echo [WARNING] Could not automatically copy the launcher to the startup folder.
    echo You may need to do this manually by typing 'shell:startup' in the Run dialog (Win+R).
) else (
    echo Invisible launcher successfully placed in your startup folder.
)
echo.
echo =================================================================
echo                       SETUP COMPLETE!
echo =================================================================
echo.
echo Your AI World is now configured. It will launch silently
echo the next time you restart your PC. You can close this window.
echo.
pause