import os

class Config:
    """
    Handles loading and providing configuration variables from the environment.
    """
    def __init__(self):
        # Discord Credentials
        self.discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
        self.discord_guild_id = int(os.getenv("DISCORD_GUILD_ID"))
        self.user_id = int(os.getenv("USER_ID"))

        # AI Service URLs
        self.ollama_api_url = os.getenv("OLLAMA_API_URL")
        self.comfyui_api_url = os.getenv("COMFYUI_API_URL")
        self.chatterbox_url = os.getenv("CHATTERBOX_URL")
        self.llm_model = os.getenv("LLM_MODEL")

        # Pinecone (Universe Memory)
        self.pinecone_api_key = os.getenv("PINECODE_API_KEY")
        self.pinecone_host = os.getenv("PINECODE_HOST")

        # Paths
        self.comfyui_path = os.getenv("COMFYUI_PATH")

        self._validate()

    def _validate(self):
        """Ensure all critical configuration variables are present."""
        critical_vars = [
            "discord_bot_token", "discord_guild_id", "user_id",
            "pinecone_api_key", "pinecone_host", "comfyui_path"
        ]
        for var in critical_vars:
            if not getattr(self, var):
                raise ValueError(f"Missing critical environment variable: {var.upper()}")