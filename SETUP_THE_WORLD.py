import os
import sys
import subprocess
import json
import winshell
from win32com.client import Dispatch

# --- Helper Functions ---
def print_header(title):
    print("\n" + "="*60)
    print(f" {title.center(58)} ")
    print("="*60)

def print_step(step, msg):
    print(f"\n[STEP {step}] {msg}")

def print_info(msg):
    print(f"  > {msg}")

def get_input(prompt):
    return input(f"  >> {prompt}: ")

def run_command(command):
    """Runs a command and streams its output."""
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"    {output.strip()}")
        rc = process.poll()
        return rc
    except Exception as e:
        print(f"  [ERROR] Failed to run command: {command}\n{e}")
        return 1

# --- Main Setup Logic ---

def install_dependencies():
    print_step(1, "Installing Python dependencies from requirements.txt...")
    if run_command(f"\"{sys.executable}\" -m pip install -r requirements.txt") != 0:
        print_info("[ERROR] Failed to install dependencies. Please check your Python/pip installation.")
        sys.exit(1)
    print_info("✅ Dependencies installed successfully.")

def configure_env_file():
    print_step(2, "Configuring secrets and environment variables...")
    if os.path.exists(".env"):
        overwrite = get_input("An .env file already exists. Overwrite? (y/n)").lower()
        if overwrite != 'y':
            print_info("Skipping .env configuration.")
            return

    token = get_input("Enter your DISCORD_BOT_TOKEN")
    guild_id = get_input("Enter your DISCORD_GUILD_ID (your server ID)")
    user_id = get_input("Enter your USER_ID (your personal Discord ID)")
    comfyui_path = get_input("Enter the full path to your ComfyUI directory (e.g., C:\\ComfyUI)")
    pinecone_key = get_input("Enter your Pinecone API Key")
    pinecone_host = get_input("Enter your Pinecone Index Host (e.g., your-index-xxxxxxx.svc.us-west1-gcp.pinecone.io)")

    with open(".env", "w") as f:
        f.write(f"DISCORD_BOT_TOKEN={token}\n")
        f.write(f"DISCORD_GUILD_ID={guild_id}\n")
        f.write(f"USER_ID={user_id}\n")
        f.write(f"COMFYUI_PATH={comfyui_path}\n")
        f.write(f"PINECONE_API_KEY={pinecone_key}\n")
        f.write(f"PINECONE_HOST={pinecone_host}\n")

    # Save comfyui path for the batch script
    os.makedirs("data", exist_ok=True)
    with open("data/.comfyui_path", "w") as f:
        f.write(comfyui_path)

    print_info("✅ .env file created successfully.")

def configure_kinks():
    print_step(3, "Configuring character kinks...")
    try:
        with open("data/character_canon.json", "r") as f:
            characters = json.load(f)
    except FileNotFoundError:
        print_info("[ERROR] `data/character_canon.json` not found. Cannot configure kinks.")
        return

    kink_data = {}
    print_info("For each character, please enter a comma-separated list of their kinks.")
    for name in characters.keys():
        kinks = get_input(f"Kinks for {name}")
        kink_data[name] = [k.strip() for k in kinks.split(",")]

    with open("data/character_kinks.json", "w") as f:
        json.dump(kink_data, f, indent=4)
    print_info("✅ Character kinks saved successfully.")

def place_startup_shortcut():
    print_step(4, "Placing invisible launcher in Windows Startup folder...")
    try:
        startup_folder = winshell.startup()
        script_path = os.path.join(os.getcwd(), "invisible_launcher.vbs")
        shortcut_path = os.path.join(startup_folder, "MyAIWorldLauncher.lnk")

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = script_path
        shortcut.WorkingDirectory = os.getcwd()
        shortcut.save()
        print_info("✅ Shortcut created successfully in your Startup folder.")
        print_info(f"   Location: {shortcut_path}")
    except Exception as e:
        print_info(f"[ERROR] Could not create startup shortcut: {e}")
        print_info("You may need to run this script as an administrator, or manually create a shortcut to 'invisible_launcher.vbs' in your startup folder.")

def main():
    print_header("My AI World - One-Time Setup")
    print("Welcome, Master. This script will configure your AI world.")
    print("Please have your secrets and paths ready.")

    install_dependencies()
    configure_env_file()
    configure_kinks()
    place_startup_shortcut()

    print_header("Setup Complete!")
    print("Your world is forged and ready.")
    print("On your next reboot, it will start silently in the background.")
    print("To start it now without rebooting, simply double-click 'start_world.bat'.")
    input("\nPress Enter to exit.")

if __name__ == "__main__":
    main()