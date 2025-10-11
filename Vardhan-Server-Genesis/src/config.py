import os
from dotenv import load_dotenv

class Config:
    """
    Handles loading and providing configuration variables from the environment.
    For this first step, it's a minimal version.
    """
    def __init__(self):
        load_dotenv()

        # Discord Credentials
        self.discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
        self.discord_guild_id = int(os.getenv("DISCORD_GUILD_ID", 0))
        self.user_id = int(os.getenv("USER_ID", 0))

        # AI Service URLs & Models
        self.ollama_api_url = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434")
        self.llm_model = os.getenv("LLM_MODEL", "dolphin-2.2.1-mistral:7b-q4_K_M")

        self._validate()

    def _validate(self):
        """Ensure all critical configuration variables are present."""
        critical_vars = [
            "discord_bot_token", "discord_guild_id", "user_id"
        ]
        missing_vars = [var for var in critical_vars if not getattr(self, var)]

        if missing_vars:
            raise ValueError(f"CRITICAL ERROR: Missing required environment variables: {', '.join(missing_vars)}. Please create a .env file.")

        if self.discord_guild_id == 0 or self.user_id == 0:
            raise ValueError("CRITICAL ERROR: DISCORD_GUILD_ID and USER_ID must be valid numbers, not 0.")

config = Config()