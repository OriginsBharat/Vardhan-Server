@echo off
ECHO.
ECHO ======================================================
ECHO  My AI World - Setup Launcher
ECHO ======================================================
ECHO.
ECHO This will first install all necessary packages.
ECHO This may take a few minutes. Please be patient.
ECHO.

REM Use 'python -m pip' for a more robust installation
python -m pip install -r requirements.txt

IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [FATAL ERROR] Failed to install required packages.
    ECHO Please check your Python installation and internet connection.
    ECHO Setup cannot continue.
    pause
    exit /b
)

ECHO.
ECHO Dependencies installed successfully.
ECHO Launching the graphical setup wizard now...
ECHO.

python SETUP_THE_WORLD.py

ECHO.
ECHO Setup finished. This window can now be closed.
pause