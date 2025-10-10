@echo off
ECHO.
ECHO ======================================================
ECHO  My AI World - Setup Launcher
ECHO ======================================================
ECHO.
ECHO This will first install all necessary packages,
ECHO and then launch the graphical setup wizard.
ECHO.

pip install -r requirements.txt

ECHO.
ECHO Launching the setup wizard now...
ECHO.

python SETUP_THE_WORLD.py

ECHO.
ECHO Setup finished. This window can now be closed.
pause