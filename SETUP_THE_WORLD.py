import os
import sys
import subprocess
import ctypes
import shutil

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_input(prompt, default=None):
    """Get input from the user with an optional default value."""
    while True:
        if default:
            response = input(f"{prompt} (optional, press Enter to use '{default}'): ").strip()
            if not response:
                return default
        else:
            response = input(f"{prompt}: ").strip()

        if response:
            return response
        else:
            print("This field is required. Please provide a value.")

def create_env_file():
    """Create the .env file with user-provided credentials."""
    print("\n--- Step 1: Discord & Pinecone Configuration ---")
    print("Please provide your secret credentials. These will be stored locally in a .env file.")

    bot_token = get_input("Enter your DISCORD_BOT_TOKEN")
    guild_id = get_input("Enter your DISCORD_GUILD_ID (your server ID)")
    user_id = get_input("Enter your USER_ID (your personal Discord ID)")
    pinecone_api_key = get_input("Enter your Pinecone API Key")
    pinecone_host = get_input("Enter your Pinecone Index Host URL")

    print("\nNext, please provide the full paths to your AI engine folders.")
    comfyui_path = get_input("Enter the full path to your ComfyUI folder (e.g., C:\\MyAIWorld\\ComfyUI)")

    env_content = f"""
DISCORD_BOT_TOKEN={bot_token}
DISCORD_GUILD_ID={guild_id}
USER_ID={user_id}
PINECODE_API_KEY={pinecone_api_key}
PINECODE_HOST={pinecone_host}
COMFYUI_PATH={comfyui_path}
OLLAMA_API_URL=http://127.0.0.1:11434
COMFYUI_API_URL=http://127.0.0.1:8188
CHATTERBOX_URL=http://127.0.0.1:7860
LLM_MODEL=dolphin-2.2.1-mistral:7b-q4_K_M
"""
    with open(".env", "w") as f:
        f.write(env_content)
    print("\n✅ .env file created successfully.")

def install_dependencies():
    """Install required Python packages using pip."""
    print("\n--- Step 2: Installing Python Dependencies ---")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\n✅ All Python packages installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERROR: Failed to install Python packages. Please check your internet connection and try again. Details: {e}")
        sys.exit(1)

def create_startup_scripts():
    """Create the batch and VBS scripts for automatic, invisible startup."""
    print("\n--- Step 3: Creating Startup Scripts ---")

    # Create start_world.bat
    start_script_content = f"""@echo off
REM This script silently starts all AI engines and the main bot application.

REM Start Ollama (if not already running as a service)
echo "Starting Ollama..."
start /B "" "C:\\Program Files\\Ollama\\ollama-app.exe"
timeout /t 5 > nul

REM Start ComfyUI
echo "Starting ComfyUI..."
cd /d "{get_input('Confirm ComfyUI Path', os.getenv('COMFYUI_PATH'))}"
start /B "" python.exe main.py --listen --port 8188
timeout /t 10 > nul

REM Start the main bot application
echo "Starting the AI World..."
cd /d "{os.path.dirname(os.path.abspath(__file__))}"
python.exe src/main.py

"""
    with open("start_world.bat", "w") as f:
        f.write(start_script_content)
    print("✅ start_world.bat created.")

    # Create invisible_launcher.vbs
    vbs_content = f"""
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "{os.path.abspath('start_world.bat')}" & Chr(34), 0
Set WshShell = Nothing
"""
    with open("invisible_launcher.vbs", "w") as f:
        f.write(vbs_content)
    print("✅ invisible_launcher.vbs created.")

def setup_auto_startup():
    """Place the launcher shortcut in the Windows Startup folder."""
    print("\n--- Step 4: Setting Up Automatic Startup ---")
    if not is_admin():
        print("⚠️ This script is not running as an administrator.")
        print("I cannot automatically place the launcher in the Startup folder.")
        print("Please manually create a shortcut to 'invisible_launcher.vbs' and place it in:")
        print(f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        input("Press Enter to continue once you have done this manually...")
        return

    try:
        startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
        shortcut_path = os.path.join(startup_folder, "MyAIWorldLauncher.lnk")

        # Using a safer method to create shortcut
        import winshell
        from win32com.client import Dispatch

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = os.path.abspath("invisible_launcher.vbs")
        shortcut.WorkingDirectory = os.path.dirname(os.path.abspath("invisible_launcher.vbs"))
        shortcut.save()

        print(f"✅ Shortcut created in Startup folder: {shortcut_path}")
    except Exception as e:
        print(f"❌ ERROR: Failed to create startup shortcut: {e}")
        print("Please create the shortcut manually as described above.")

def main():
    """Main function to run the setup process."""
    print("=================================================")
    print("    Welcome to the My AI World Setup Script    ")
    print("=================================================")
    print("This script will guide you through a one-time setup.")

    # Check for admin rights
    if not is_admin():
        print("\n[WARNING] For automatic startup, it's best to run this script as an administrator.")
        print("Right-click the file and select 'Run as administrator'.")
        if get_input("Continue without admin rights? (y/n)", "n").lower() != 'y':
            sys.exit()

    create_env_file()
    install_dependencies()
    create_startup_scripts()
    setup_auto_startup()

    print("\n=================================================")
    print("          ✅ SETUP COMPLETE! ✅")
    print("=================================================")
    print("Your world is now configured. It will start automatically the next time you boot your PC.")
    print("To start it now, you can run the 'start_world.bat' file.")
    input("\nPress Enter to exit.")

if __name__ == "__main__":
    # Load environment variables to assist with defaults
    from dotenv import load_dotenv
    load_dotenv()
    main()