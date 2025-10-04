# src/config.py
# Handles loading and validation of all configuration variables from the .env file.

import os
from dotenv import load_dotenv
import logging

class Config:
    """
    A class to hold all configuration variables, loaded from a .env file.
    It provides a single, validated source of truth for all secrets and settings.
    """
    def __init__(self):
        # Explicitly define the path to the .env file in the project root.
        # This makes the application robust, regardless of where it's launched from.
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dotenv_path = os.path.join(project_root, '.env')

        if not os.path.exists(dotenv_path):
             raise ValueError(f"CRITICAL ERROR: .env file not found at path: {dotenv_path}")

        load_dotenv(dotenv_path=dotenv_path)

        # --- Discord Secrets ---
        self.DISCORD_BOT_TOKEN: str = self._get_env("DISCORD_BOT_TOKEN")
        self.DISCORD_GUILD_ID: int = int(self._get_env("DISCORD_GUILD_ID"))
        self.USER_ID: int = int(self._get_env("USER_ID"))
        self.DISCORD_EVENT_CHANNEL_ID: int = int(self._get_env("DISCORD_EVENT_CHANNEL_ID"))
        self.DISCORD_CONTROL_CHANNEL_ID: int = int(self._get_env("DISCORD_CONTROL_CHANNEL_ID"))
        self.DISCORD_AUCTION_CHANNEL_ID: int = int(self._get_env("DISCORD_AUCTION_CHANNEL_ID"))

        # --- Self-Hosted AI Service URLs ---
        self.OLLAMA_API_URL: str = self._get_env("OLLAMA_API_URL", "http://127.0.0.1:11434")
        self.COMFYUI_API_URL: str = self._get_env("COMFYUI_API_URL", "http://127.0.0.1:8188")
        self.XTTS_API_URL: str = self._get_env("XTTS_API_URL", "http://127.0.0.1:8010")

        # --- VPS Portability ---
        self.TRIAL_END_DATE: str = self._get_env("TRIAL_END_DATE", "")

        logging.info("Configuration loaded and validated.")

    def _get_env(self, key: str, default: str = None) -> str:
        """
        Retrieves an environment variable, raising an error if it's not found and no default is provided.
        Also checks for placeholder values.
        """
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"CRITICAL ERROR: Missing required environment variable '{key}'. Please check your .env file.")

        if "YOUR_" in value:
            # This is a special check for the initial setup. We will allow FAKE_TOKEN for testing.
            if key == "DISCORD_BOT_TOKEN" and value == "FAKE_TOKEN_FOR_TESTING":
                pass
            else:
                raise ValueError(f"CRITICAL ERROR: Placeholder value for '{key}' found. Please fill in your actual credentials in the .env file.")

        return value