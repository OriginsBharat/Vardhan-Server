import os
import json

def print_header(title):
    print("=" * 65)
    print(f"  {title}")
    print("=" * 65)
    print()

def get_user_input(prompt):
    return input(prompt).strip()

def main():
    # --- .env Configuration ---
    print_header("Step 1 of 2: World Configuration (.env file)")
    print("I will now ask for your secrets and configuration details.")
    print("This information will be saved locally in your .env file.")
    print()

    discord_bot_token = get_user_input("Enter your DISCORD_BOT_TOKEN: ")
    discord_guild_id = get_user_input("Enter your DISCORD_GUILD_ID (Server ID): ")
    user_id = get_user_input("Enter your USER_ID: ")
    comfyui_path = get_user_input("Enter the FULL PATH to your ComfyUI_windows_portable folder: ")
    pinecone_api_key = get_user_input("Enter your Pinecone API Key: ")
    pinecone_index_host = get_user_input("Enter your Pinecone Index Host: ")

    env_content = f"""
DISCORD_BOT_TOKEN={discord_bot_token}
DISCORD_GUILD_ID={discord_guild_id}
USER_ID={user_id}
COMFYUI_PATH={comfyui_path}
PINECONE_API_KEY={pinecone_api_key}
PINECONE_INDEX_HOST={pinecone_index_host}
OLLAMA_API_URL=http://127.0.0.1:11434
COMFYUI_API_URL=http://127.0.0.1:8188
"""
    with open(".env", "w") as f:
        f.write(env_content)

    print("\n[OK] Configuration saved to .env file.")
    print("-" * 65)

    # --- Kink Configuration ---
    print_header("Step 2 of 2: Interactive Kink Customization")
    print("For each character, please provide a SPACE-separated list of their kinks.")
    print("For kinks with multiple words, please use an underscore (e.g., mind_control).")
    print()

    if not os.path.exists("data"):
        os.makedirs("data")

    characters = ["Maya", "Eka", "Dvi", "Tri", "Chatur", "Panch", "Shash", "Sapt", "Asht", "Nav", "Dash"]
    kink_data = {}

    for char_name in characters:
        kinks_input = get_user_input(f"Enter kinks for {char_name}: ")
        kink_list = [k.strip() for k in kinks_input.split()]
        kink_data[char_name] = {"kinks": kink_list}

    with open("data/character_kinks.json", "w") as f:
        json.dump(kink_data, f, indent=4)

    print("\n[OK] Master's Directives for kinks have been saved to data/character_kinks.json.")
    print("-" * 65)
    print("\nInteractive setup complete!")

if __name__ == "__main__":
    main()