import os

class Config:
    """
    Handles loading and providing configuration variables from the environment.
    """
    def __init__(self):
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

        # Paths
        self.comfyui_path = os.getenv("COMFYUI_PATH")

        self._validate()

    def _validate(self):
        """Ensure all critical configuration variables are present."""
        critical_vars = [
            "discord_bot_token", "discord_guild_id", "user_id",
            "pinecone_api_key", "pinecone_host", "comfyui_path"
        ]
        for var_name in critical_vars:
            value = getattr(self, var_name)
            if not value:
                raise ValueError(f"CRITICAL ERROR: Missing required environment variable '{var_name.upper()}' in your .env file.")
            if isinstance(value, int) and value == 0:
                 raise ValueError(f"CRITICAL ERROR: Environment variable '{var_name.upper()}' must be a valid ID, not 0.")