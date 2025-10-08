import os
from dotenv import load_dotenv

class Config:
    """Loads and holds all configuration variables for the application."""
    def __init__(self):
        # Load environment variables from a .env file
        load_dotenv()

        # Discord Secrets (must be provided)
        self.discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
        self.guild_id = int(os.getenv("DISCORD_GUILD_ID", 0))
        self.user_id = int(os.getenv("USER_ID", 0))

        # Critical Paths (must be provided)
        self.comfyui_path = os.getenv("COMFYUI_PATH")

        # Pinecone Cloud Memory (must be provided)
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_index_host = os.getenv("PINECONE_INDEX_HOST")

        # AI Service URLs (sensible defaults)
        self.ollama_api_url = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434")
        self.comfyui_api_url = os.getenv("COMFYUI_API_URL", "http://127.0.0.1:8188")

        # Channel IDs (will be found at runtime by the bot)
        self.event_channel_id = None
        self.control_channel_id = None
        self.auction_channel_id = None
        self.courthouse_channel_id = None
        self.bank_channel_id = None

        self._validate()

    def _validate(self):
        """Ensures all critical configuration variables are present."""
        critical_vars = [
            "discord_bot_token",
            "guild_id",
            "user_id",
            "comfyui_path",
            "pinecone_api_key",
            "pinecone_index_host",
        ]
        missing_vars = [var for var in critical_vars if not getattr(self, var)]
        if missing_vars:
            raise ValueError(f"Missing critical configuration variables: {', '.join(missing_vars)}")

        if self.guild_id == 0 or self.user_id == 0:
            raise ValueError("DISCORD_GUILD_ID and USER_ID must be valid integers.")