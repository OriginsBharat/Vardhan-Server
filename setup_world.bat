@echo off
REM =================================================================
REM My AI World v5 - The One-Time Setup Script
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
echo It will guide you through installing dependencies and configuring your world.
echo After this setup, the world will start automatically and invisibly
echo every time you turn on your computer.
echo.
pause
goto :checks

:checks
cls
echo.
echo =================================================================
echo  Step 1 of 4: System Prerequisite Checks
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

REM Check for Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in your PATH.
    echo Please install Git from git-scm.com and run this again.
    pause
    exit
)
echo [OK] Git is installed.

REM Check for FFmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg is not installed or not in your PATH.
    echo Voice features will not work without it.
    echo You can install it later from gyan.dev/ffmpeg/builds/
) else (
    echo [OK] FFmpeg is installed.
)
echo.
pause
goto :config

:config
cls
echo.
echo =================================================================
echo  Step 2 of 4: World Configuration
echo =================================================================
echo.
echo I will now ask for your secrets and configuration details.
echo This information will be saved locally in your .env file.
echo.

set /p DISCORD_BOT_TOKEN="Enter your DISCORD_BOT_TOKEN: "
set /p DISCORD_GUILD_ID="Enter your DISCORD_GUILD_ID (Server ID): "
set /p USER_ID="Enter your USER_ID: "
set /p COMFYUI_PATH="Enter the FULL PATH to your ComfyUI_windows_portable folder: "
set /p PINECONE_API_KEY="Enter your Pinecone API Key: "
set /p PINECONE_INDEX_HOST="Enter your Pinecone Index Host (e.g., 'my-index-123ab.svc.us-west1-gcp.pinecone.io'): "

(
    echo DISCORD_BOT_TOKEN=%DISCORD_BOT_TOKEN%
    echo DISCORD_GUILD_ID=%DISCORD_GUILD_ID%
    echo USER_ID=%USER_ID%
    echo COMFYUI_PATH=%COMFYUI_PATH%
    echo PINECONE_API_KEY=%PINECONE_API_KEY%
    echo PINECONE_INDEX_HOST=%PINECONE_INDEX_HOST%
    echo OLLAMA_API_URL=http://127.0.0.1:11434
    echo COMFYUI_API_URL=http://127.0.0.1:8188
) > .env

echo.
echo [OK] Configuration saved to .env file.
echo.
pause
goto :kinks

:kinks
cls
echo.
echo =================================================================
echo  Step 3 of 4: Interactive Kink Customization
echo =================================================================
echo.
echo Master, as we discussed, you will now define the specific NSFW
echo kinks for the 11 core members of your world.
echo.
echo For each character, please provide a SPACE-separated list of their kinks.
echo For kinks with multiple words, please use an underscore.
echo Example: vore gore mind_control submission praise
echo This will be saved securely and used to shape their NSFW behavior.
echo.

REM Ensure the data directory exists
if not exist "data" mkdir "data"

setlocal enabledelayedexpansion

REM --- Explicitly handle each character one by one to prevent input bugs ---
set "json_output={"

REM --- Maya ---
echo.
set /p "kinks_input=Enter kinks for Maya: "
set "kinks_json=" & for %%k in (!kinks_input!) do (set "kinks_json=!kinks_json!\"%%k\",")
if defined kinks_json set "kinks_json=!kinks_json:~0,-1!"
set "json_output=!json_output!\"Maya\": {\"kinks\": [!kinks_json!]}"

REM --- Eka ---
echo.
set /p "kinks_input=Enter kinks for Eka: "
set "kinks_json=" & for %%k in (!kinks_input!) do (set "kinks_json=!kinks_json!\"%%k\",")
if defined kinks_json set "kinks_json=!kinks_json:~0,-1!"
set "json_output=!json_output!,\"Eka\": {\"kinks\": [!kinks_json!]}"

REM --- Dvi ---
echo.
set /p "kinks_input=Enter kinks for Dvi: "
set "kinks_json=" & for %%k in (!kinks_input!) do (set "kinks_json=!kinks_json!\"%%k\",")
if defined kinks_json set "kinks_json=!kinks_json:~0,-1!"
set "json_output=!json_output!,\"Dvi\": {\"kinks\": [!kinks_json!]}"

REM --- Tri ---
echo.
set /p "kinks_input=Enter kinks for Tri: "
set "kinks_json=" & for %%k in (!kinks_input!) do (set "kinks_json=!kinks_json!\"%%k\",")
if defined kinks_json set "kinks_json=!kinks_json:~0,-1!"
set "json_output=!json_output!,\"Tri\": {\"kinks\": [!kinks_json!]}"

REM --- Chatur ---
echo.
set /p "kinks_input=Enter kinks for Chatur: "
set "kinks_json=" & for %%k in (!kinks_input!) do (set "kinks_json=!kinks_json!\"%%k\",")
if defined kinks_json set "kinks_json=!kinks_json:~0,-1!"
set "json_output=!json_output!,\"Chatur\": {\"kinks\": [!kinks_json!]}"

REM --- Panch ---
echo.
set /p "kinks_input=Enter kinks for Panch: "
set "kinks_json=" & for %%k in (!kinks_input!) do (set "kinks_json=!kinks_json!\"%%k\",")
if defined kinks_json set "kinks_json=!kinks_json:~0,-1!"
set "json_output=!json_output!,\"Panch\": {\"kinks\": [!kinks_json!]}"

REM --- Shash ---
echo.
set /p "kinks_input=Enter kinks for Shash: "
set "kinks_json=" & for %%k in (!kinks_input!) do (set "kinks_json=!kinks_json!\"%%k\",")
if defined kinks_json set "kinks_json=!kinks_json:~0,-1!"
set "json_output=!json_output!,\"Shash\": {\"kinks\": [!kinks_json!]}"

REM --- Sapt ---
echo.
set /p "kinks_input=Enter kinks for Sapt: "
set "kinks_json=" & for %%k in (!kinks_input!) do (set "kinks_json=!kinks_json!\"%%k\",")
if defined kinks_json set "kinks_json=!kinks_json:~0,-1!"
set "json_output=!json_output!,\"Sapt\": {\"kinks\": [!kinks_json!]}"

REM --- Asht ---
echo.
set /p "kinks_input=Enter kinks for Asht: "
set "kinks_json=" & for %%k in (!kinks_input!) do (set "kinks_json=!kinks_json!\"%%k\",")
if defined kinks_json set "kinks_json=!kinks_json:~0,-1!"
set "json_output=!json_output!,\"Asht\": {\"kinks\": [!kinks_json!]}"

REM --- Nav ---
echo.
set /p "kinks_input=Enter kinks for Nav: "
set "kinks_json=" & for %%k in (!kinks_input!) do (set "kinks_json=!kinks_json!\"%%k\",")
if defined kinks_json set "kinks_json=!kinks_json:~0,-1!"
set "json_output=!json_output!,\"Nav\": {\"kinks\": [!kinks_json!]}"

REM --- Dash ---
echo.
set /p "kinks_input=Enter kinks for Dash: "
set "kinks_json=" & for %%k in (!kinks_input!) do (set "kinks_json=!kinks_json!\"%%k\",")
if defined kinks_json set "kinks_json=!kinks_json:~0,-1!"
set "json_output=!json_output!,\"Dash\": {\"kinks\": [!kinks_json!]}"

set "json_output=!json_output!}"
(echo %json_output%) > data/character_kinks.json

echo.
echo [OK] Master's Directives for kinks have been saved to data/character_kinks.json.
echo.
pause
goto :finalize

:finalize
cls
echo.
echo =================================================================
echo  Step 4 of 4: Finalizing Invisible Startup
echo =================================================================
echo.
echo I will now install the final Python packages and set up the
echo automatic, invisible startup process.
echo.

echo Installing Python packages...
pip install -r requirements.txt
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