@echo off
REM =================================================================
REM My AI World v5 - The One-Time Setup Script (Simplified)
REM =================================================================
REM Master, run this script only ONCE. It will guide you through
REM the complete setup and configuration of your invisible AI world.
REM =================================================================

:start
cls
echo.
echo =================================================================
echo  Welcome to the My AI World v5 Setup
echo =================================================================
echo.
echo This script will perform a one-time setup to bring your world to life.
echo.
pause
goto :checks

:checks
cls
echo.
echo =================================================================
echo  Step 1 of 3: System Prerequisite Checks
echo =================================================================
echo.
echo I will now check if you have the necessary software installed.
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10 or higher from python.org and run this again.
    pause
    exit
)
echo [OK] Python is installed.
echo.
pause
goto :interactive_setup

:interactive_setup
cls
echo.
echo =================================================================
echo  Step 2 of 3: Interactive Configuration
echo =================================================================
echo.
echo I will now launch the interactive Python setup script.
echo Please answer the questions in the new window that appears.
echo.

python src/interactive_setup.py

if %errorlevel% neq 0 (
    echo [ERROR] The interactive setup script failed. Please check for errors above.
    pause
    exit
)

echo.
echo [OK] Interactive setup complete.
echo.
pause
goto :finalize

:finalize
cls
echo.
echo =================================================================
echo  Step 3 of 3: Finalizing Invisible Startup
echo =================================================================
echo.
echo I will now install the final Python packages and set up the
echo automatic, invisible startup process.
echo.

echo Installing Python packages...
echo.
echo Creating a local Python virtual environment to bypass system issues...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create a Python virtual environment. Please check your Python installation.
    pause
    exit
)
echo.
echo Installing packages into the new virtual environment...
venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python packages into the virtual environment. Please check requirements.txt and your connection.
    pause
    exit
)
echo.

echo Creating invisible launcher shortcut in your Windows Startup folder...
set "startup_folder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "shortcut_path=%startup_folder%\MyAIWorld.lnk"
set "target_path=%~dp0invisible_launcher.vbs"

(
    echo Set oWS = WScript.CreateObject("WScript.Shell")
    echo sLinkFile = "%shortcut_path%"
    echo Set oLink = oWS.CreateShortcut(sLinkFile)
    echo oLink.TargetPath = "%target_path%"
    echo oLink.Save
) > create_shortcut.vbs

cscript //nologo create_shortcut.vbs
del create_shortcut.vbs

echo.
echo [OK] Invisible startup has been configured.
echo.
pause
cls
echo.
echo =================================================================
echo  SETUP COMPLETE
echo =================================================================
echo.
echo The one-time setup is finished. Your AI world will now start for
echo the first time.
echo.
echo From now on, it will start automatically and silently with your PC.
echo There is nothing more you need to do.
echo.
echo Your world is now alive.
echo.
pause

REM --- Launch for the first time ---
start "" /B "invisible_launcher.vbs"

exit