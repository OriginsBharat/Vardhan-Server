import os
from dotenv import load_dotenv

class Config:
    """
    Handles loading and providing configuration variables from the environment.
    """
    def __init__(self):
        load_dotenv()

        # Discord Credentials
        self.discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
        self.discord_guild_id = int(os.getenv("DISCORD_GUILD_ID", 0))
        self.user_id = int(os.getenv("USER_ID", 0))

        # AI Service URLs & Models
        self.ollama_api_url = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434")
        self.comfyui_api_url = os.getenv("COMFYUI_API_URL", "http://127.0.0.1:8188")
        self.chatterbox_url = os.getenv("CHATTERBOX_URL", "http://127.0.0.1:7860") # Kept for consistency
        self.llm_model = os.getenv("LLM_MODEL", "dolphin-2.2.1-mistral:7b-q4_K_M")

        # Pinecone (Universe Memory)
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_host = os.getenv("PINECONE_HOST")

        # Path to ComfyUI, read from the file created by the setup script
        self.comfyui_path = self._get_comfyui_path()

        self._validate()

    def _get_comfyui_path(self):
        path_file = "data/.comfyui_path"
        if os.path.exists(path_file):
            with open(path_file, "r") as f:
                return f.read().strip()
        return os.getenv("COMFYUI_PATH") # Fallback to .env for manual setup

    def _validate(self):
        """Ensure all critical configuration variables are present."""
        critical_vars = {
            "discord_bot_token": "Your Discord bot's unique token.",
            "discord_guild_id": "The ID of the Discord server where the bot will live.",
            "user_id": "Your personal Discord user ID for Master permissions.",
            "pinecone_api_key": "Your API key from pinecone.io for cloud memory.",
            "pinecone_host": "The index host URL from pinecone.io.",
            "comfyui_path": "The full path to your ComfyUI installation."
        }
        missing_vars = []
        for var_name, description in critical_vars.items():
            value = getattr(self, var_name)
            if not value or (isinstance(value, int) and value == 0):
                missing_vars.append(f"- {var_name.upper()}: {description}")

        if missing_vars:
            error_message = "CRITICAL ERROR: The following required settings are missing.\nPlease run SETUP_THE_WORLD.py or manually create your .env file:\n" + "\n".join(missing_vars)
            raise ValueError(error_message)