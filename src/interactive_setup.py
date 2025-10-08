import json
import os
from pathlib import Path

def get_input(prompt, is_secret=False):
    """Gets user input with a clear prompt."""
    # In a real GUI, this could be a password field.
    return input(f"> {prompt}: ")

def create_env_file():
    """Guides the user through creating the .env file."""
    print("--- Step 1 of 2: System Configuration ---")
    print("I will now ask for your Discord credentials, API keys, and local paths.")
    print("Please have them ready. You can right-click to paste in this window.\n")

    # Discord Secrets
    token = get_input("Enter your DISCORD_BOT_TOKEN")
    guild_id = get_input("Enter your DISCORD_GUILD_ID (your server's ID)")
    user_id = get_input("Enter your USER_ID (your personal Discord ID)")

    # Local Paths
    print("\nNow, please provide the full paths to your AI engine folders.")
    comfyui_path = get_input(r"Enter the full path to your ComfyUI folder (e.g., C:\MyAIWorld\ComfyUI)")

    # Pinecone API
    print("\nNext, let's set up the cloud memory (Pinecone).")
    print("Please go to https://pinecone.io, sign up for a free 'Starter' account,")
    print("create a new index with dimension 384 and metric 'cosine', then find your API keys.")
    pinecone_key = get_input("Enter your Pinecone API Key")
    pinecone_host = get_input("Enter your Pinecone Index Host (e.g., your-index-name-12345.svc.gcp-starter.pinecone.io)")

    env_content = f"""# Discord Secrets
DISCORD_BOT_TOKEN={token}
DISCORD_GUILD_ID={guild_id}
USER_ID={user_id}

# Full path to the ComfyUI installation directory
COMFYUI_PATH={comfyui_path}

# API URLs for running servers (defaults are usually correct)
OLLAMA_API_URL=http://127.0.0.1:11434
COMFYUI_API_URL=http://127.0.0.1:8188

# Pinecone Cloud Memory
PINECONE_API_KEY={pinecone_key}
PINECONE_INDEX_HOST={pinecone_host}
"""
    with open(".env", "w") as f:
        f.write(env_content.strip())
    print("\n.env file created successfully.")

def create_kink_file():
    """Guides the user through setting character kinks."""
    print("\n--- Step 2 of 2: Character Kink Customization ---")
    print("For each character, please provide a comma-separated list of their kinks.")
    print("For kinks with multiple words, please use an underscore (e.g., mind_control, public_humiliation).")
    print("Press Enter after each character's list.\n")

    characters = ["Maya", "Eka", "Dvi", "Tri", "Chatur", "Panch", "Shash", "Sapt", "Asht", "Nav", "Dash"]
    kink_data = {}

    for char in characters:
        kinks_str = get_input(f"Enter kinks for {char}")
        # Sanitize by replacing spaces with underscores in each kink
        kinks_list = [k.strip().replace(" ", "_") for k in kinks_str.split(',')]
        kink_data[char] = kinks_list

    kink_file_path = Path("data/character_kinks.json")
    kink_file_path.parent.mkdir(exist_ok=True, parents=True)
    with open(kink_file_path, "w") as f:
        json.dump(kink_data, f, indent=4)
    print("\nCharacter kinks saved successfully.")

if __name__ == "__main__":
    try:
        print("=================================================================")
        print(" Welcome to the One-Time Interactive Setup for Your AI World")
        print("=================================================================")
        create_env_file()
        create_kink_file()
        print("\n[SUCCESS] Interactive setup is complete!")
        print("The main batch script will now finalize the installation.")
        print("=================================================================")
    except Exception as e:
        print(f"\n[FATAL ERROR] The interactive setup failed: {e}")
        input("Press Enter to exit.")