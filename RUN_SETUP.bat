@echo off
chcp 65001 > nul

ECHO.
ECHO ==================================================================
ECHO  Welcome to the My AI World Setup
ECHO ==================================================================
ECHO.
ECHO This script will prepare your system to bring your AI world to life.
ECHO It will install all necessary Python packages and then launch the
ECHO graphical setup wizard.
ECHO.
ECHO This may take a few minutes. Please be patient.
ECHO.
ECHO Press any key to begin the installation...
pause > nul
ECHO.
ECHO Installing dependencies from requirements.txt...

:: Use py -m pip for maximum compatibility on Windows systems
py -m pip install -r requirements.txt

:: Check if the installation was successful
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [FATAL ERROR] Failed to install required Python packages.
    ECHO.
    ECHO Please ensure you have Python installed and that it's added to your PATH.
    ECHO You can download Python from: https://www.python.org/downloads/
    ECHO.
    ECHO Setup cannot continue.
    pause
    exit /b
)

ECHO.
ECHO Dependencies installed successfully!
ECHO.
ECHO ==================================================================
ECHO  Launching Graphical Setup Wizard...
ECHO ==================================================================
ECHO.

:: Now, run the main setup script
py SETUP_THE_WORLD.py

ECHO.
ECHO ==================================================================
ECHO  Setup Complete
ECHO ==================================================================
ECHO.
ECHO The setup wizard has finished. This window can now be closed.
ECHO.
pause