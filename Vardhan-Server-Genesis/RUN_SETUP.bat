@echo off
title My AI World - Setup Launcher
echo =================================================================
echo             MY AI WORLD - SETUP & INSTALLATION
echo =================================================================
echo.
echo This script will first install all necessary Python packages,
echo and then launch the graphical setup wizard.
echo.
echo Please ensure you are connected to the internet.
echo This process may take several minutes.
echo.
echo =================================================================
pause
echo.

echo [PHASE 1/2] Installing required Python packages...
echo.

python -m pip install --upgrade pip
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Could not upgrade pip using 'python -m pip'.
    echo This might be okay. Trying to install packages anyway...
    echo.
)

python -m pip install -r requirements.txt

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    echo  FATAL ERROR: Failed to install Python packages.
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    echo.
    echo  Please ensure Python is installed correctly (with the 'Add to PATH'
    echo  option checked) and you have an internet connection.
    echo  Try running this script as an administrator.
    echo.
    pause
    exit /b 1
)

echo.
echo [PHASE 1/2] Package installation successful!
echo.
echo =================================================================
echo.
echo [PHASE 2/2] Launching the graphical setup wizard...
echo.

python SETUP_THE_WORLD.py

echo.
echo =================================================================
echo  Setup has finished. You can now close this window.
echo =================================================================
echo.
pause