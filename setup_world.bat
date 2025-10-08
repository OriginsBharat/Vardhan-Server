@echo off
echo =================================================================
echo  Welcome to the One-Time Setup for Your AI World
echo =================================================================
echo.
echo This script will guide you through the configuration and then
echo set up your world to run automatically and invisibly
echo every time you start your PC.
echo.
echo Press any key to begin the setup...
pause > nul

cls
echo =================================================================
echo  Step 1 of 3: Creating a Safe Python Environment
echo =================================================================
echo.
echo I will now create a local Python virtual environment (venv).
echo This ensures the AI world's dependencies do not conflict
echo with any other Python software on your system.
echo.

python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create Python virtual environment.
    echo Please ensure Python 3.10+ is installed and in your PATH.
    pause
    exit /b 1
)
echo.
echo Virtual environment created successfully in the 'venv' folder.
echo.
echo Press any key to continue...
pause > nul

cls
echo =================================================================
echo  Step 2 of 3: Interactive Configuration
echo =================================================================
echo.
echo I will now launch the interactive Python setup script.
echo Please answer the questions in the new window that appears.
echo.

call venv\Scripts\python.exe src/interactive_setup.py
if %errorlevel% neq 0 (
    echo [ERROR] The interactive setup script failed. Please check for errors above.
    pause
    exit /b 1
)
echo.
echo Configuration saved.
echo.
echo Press any key to continue...
pause > nul

cls
echo =================================================================
echo  Step 3 of 3: Finalizing Invisible Startup
echo =================================================================
echo.
echo I will now install the final Python packages and set up the
echo automatic, invisible startup process.
echo.
echo Installing Python packages...
echo This may take several minutes depending on your internet connection.
echo.

call venv\Scripts\pip.exe install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python packages into the virtual environment.
    echo Please check requirements.txt and your connection.
    pause
    exit /b 1
)
echo.
echo All packages installed successfully.
echo.
echo Creating startup scripts...

:: Create the main startup batch file
(
    echo @echo off
    echo echo Starting Ollama Server...
    echo start /B ollama serve
    echo.
    echo echo Starting ComfyUI Server...
    set /p COMFYUI_PATH=<.env
    for /f "tokens=1,* delims==" %%a in ('findstr "COMFYUI_PATH" .env') do set COMFYUI_PATH=%%b
    echo start /B "" "%COMFYUI_PATH%\python_embeded\python.exe" -s "%COMFYUI_PATH%\main.py" --windows-standalone-build
    echo.
    echo echo Waiting for AI engines to initialize...
    echo timeout /t 15 > nul
    echo.
    echo echo Starting the AI World Bot...
    echo call venv\Scripts\python.exe src\main.py
) > start_world.bat

:: Create the VBScript for invisible execution
(
    echo Set WshShell = CreateObject("WScript.Shell"^)
    echo WshShell.Run "cmd /c start_world.bat", 0
    echo Set WshShell = Nothing
) > invisible_launcher.vbs

echo Startup scripts created.
echo.
echo Placing launcher in Windows Startup folder for automatic execution...

set STARTUP_PATH="%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
copy invisible_launcher.vbs %STARTUP_PATH% > nul
if %errorlevel% neq 0 (
    echo [WARNING] Could not automatically copy the launcher to the startup folder.
    echo You may need to do this manually for the world to start with your PC.
    echo You can find the startup folder by typing 'shell:startup' in the Run dialog (Win+R).
) else (
    echo Invisible launcher successfully placed in your startup folder.
)
echo.
echo =================================================================
echo                       SETUP COMPLETE!
echo =================================================================
echo.
echo Your AI World is now launching for the first time.
echo From now on, it will start automatically and silently with your PC.
echo You can close this window.
echo.
pause
start "" invisible_launcher.vbs
exit